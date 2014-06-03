# -*- coding: utf-8 -*-

"""A Python module for dealing with NUT (Network UPS Tools) servers.

* PyNUTError: Base class for custom exceptions.
* PyNUTClient: Allows connecting to and communicating with PyNUT
  servers.
"""


#   Copyright (C) 2014 george2
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# 2008-01-14 David Goncalves
#            PyNUT is an abstraction class to access NUT (Network UPS
#            Tools) server.
#
# 2008-06-09 David Goncalves
#            Added 'GetRWVars' and 'SetRWVar' commands.
#
# 2009-02-19 David Goncalves
#            Changed class PyNUT to PyNUTClient
#
# 2010-07-23 David Goncalves - Version 1.2
#            Changed GetRWVars function that fails is the UPS is not
#            providing such vars.
#
# 2011-07-05 René Martín Rodríguez <rmrodri@ull.es> - Version 1.2.1
#            Added support for FSD, HELP and VER commands
#
# 2012-02-07 René Martín Rodríguez <rmrodri@ull.es> - Version 1.2.2
#            Added support for LIST CLIENTS command
#
# 2014-06-02 george2 - Version 2.0.0
#            Refactored the API, broke backwards compatibility.
#

import telnetlib
import logging


__version__ = '2.0.0'
__all__ = ['PyNUTError', 'PyNUTClient']

logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(message)s")


class PyNUTError(Exception):
    """Base class for custom exceptions."""

class PyNUTClient(object):
    """Access NUT (Network UPS Tools) servers."""

    def __init__(self, host="127.0.0.1", port=3493, login=None, password=None, debug=False, timeout=5, connect=True):
        """Class initialization method.

        host     : Host to connect (defaults to 127.0.0.1).
        port     : Port where NUT listens for connections (defaults to 3493).
        login    : Login used to connect to NUT server (defaults to None
                   for no authentication).
        password : Password used when using authentication (defaults to None).
        debug    : Boolean, put class in debug mode (prints everything
                   on console, defaults to False).
        timeout  : Timeout used to wait for network response (defaults
                   to 5 seconds).
        """
        if debug:
            # Print DEBUG messages to the console.
            logging.getLogger().setLevel(logging.DEBUG)

        logging.debug("Class initialization...")
        logging.debug(" -> Host = %s (port %s)", host, port)
        logging.debug(" -> Login = '%s' / '%s'", login, password)

        self._host = host
        self._port = port
        self._login = login
        self._password = password
        self._timeout = timeout
        self._srv_handler = None

        if connect:
            self._connect()

    def __del__(self):
        # Try to disconnect cleanly when class is deleted.
        if self._srv_handler:
            try:
                self._srv_handler.write("LOGOUT\n")
            except telnetlib.socket.error:
                # The socket is already disconnected.
                pass
            finally:
                self._srv_handler.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_t, exc_v, trace):
        self.__del__()

    def _connect(self):
        """Connects to the defined server.

        If login/pass was specified, the class tries to authenticate.
        An error is raised if something goes wrong.
        """
        logging.debug("Connecting to host")

        self._srv_handler = telnetlib.Telnet(self._host, self._port)

        if self._login != None:
            self._srv_handler.write("USERNAME %s\n" % self._login)
            result = self._srv_handler.read_until("\n", self._timeout)
            if not result.startswith("OK"):
                raise PyNUTError(result.replace("\n", ""))

        if self._password != None:
            self._srv_handler.write("PASSWORD %s\n" % self._password)
            result = self._srv_handler.read_until("\n", self._timeout)
            if not result.startswith("OK"):
                raise PyNUTError(result.replace("\n", ""))

    def list_ups(self):
        """Returns the list of available UPS from the NUT server.

        The result is a dictionary containing 'key->val' pairs of
        'UPSName' and 'UPS Description'.
        """
        logging.debug("list_ups from server")

        self._srv_handler.write("LIST UPS\n")
        result = self._srv_handler.read_until("\n")
        if result != "BEGIN LIST UPS\n":
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until("END LIST UPS\n")

        ups_dict = {}
        for line in result.split("\n"):
            if line.startswith("UPS"):
                ups, desc = line[len("UPS "):-len('"')].split('"')[:2]
                ups_dict[ups.strip()] = desc.strip()

        return ups_dict

    def list_vars(self, ups=""):
        """Get all available vars from the specified UPS.

        The result is a dictionary containing 'key->val' pairs of all
        available vars.
        """
        logging.debug("list_vars called...")

        self._srv_handler.write("LIST VAR %s\n" % ups)
        result = self._srv_handler.read_until("\n")
        if result != "BEGIN LIST VAR %s\n" % ups:
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until("END LIST VAR %s\n" % ups)
        offset = len("VAR %s " % ups)
        end_offset = 0 - (len("END LIST VAR %s\n" % ups) + 1)

        ups_vars = {}
        for current in result[:end_offset].split("\n"):
            var, data = current[offset:].split('"')[:2]
            ups_vars[var.strip()] = data

        return ups_vars

    def list_commands(self, ups=""):
        """Get all available commands for the specified UPS.

        The result is a dict object with command name as key and a description
        of the command as value.
        """
        logging.debug("list_commands called...")

        self._srv_handler.write("LIST CMD %s\n" % ups)
        result = self._srv_handler.read_until("\n")
        if result != "BEGIN LIST CMD %s\n" % ups:
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until("END LIST CMD %s\n" % ups)
        offset = len("CMD %s " % ups)
        end_offset = 0 - (len("END LIST CMD %s\n" % ups) + 1)

        commands = {}
        for current in result[:end_offset].split("\n"):
            command = current[offset:].split('"')[0].strip()

            # For each var we try to get the available description
            try:
                self._srv_handler.write("GET CMDDESC %s %s\n" % (ups, command))
                temp = self._srv_handler.read_until("\n")
                if temp.startswith("CMDDESC"):
                    desc_offset = len("CMDDESC %s %s " % (ups, command))
                    commands[command] = temp[desc_offset:-1].split('"')[1]
                else:
                    commands[command] = command
            except IndexError:
                commands[command] = command

        return commands

    def list_clients(self, ups=None):
        """Returns the list of connected clients from the NUT server.

        The result is a dictionary containing 'key->val' pairs of
        'UPSName' and a list of clients.
        """
        logging.debug("list_clients from '%s'...", ups or "server")

        if ups and (ups not in self.list_ups()):
            raise PyNUTError("%s is not a valid UPS" % ups)

        if ups:
            self._srv_handler.write("LIST CLIENTS %s\n" % ups)
        else:
            self._srv_handler.write("LIST CLIENTS\n")
        result = self._srv_handler.read_until("\n")
        if result != "BEGIN LIST CLIENTS\n":
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until("END LIST CLIENTS\n")

        clients = {}
        for line in result.split("\n"):
            if line.startswith("CLIENT"):
                host, ups = line[len("CLIENT "):].split(' ')[:2]
                if not ups in clients:
                    clients[ups] = []
                clients[ups].append(host)

        return clients

    def list_rw_vars(self, ups=""):
        """Get a list of all writable vars from the selected UPS.

        The result is presented as a dictionary containing 'key->val'
        pairs.
        """
        logging.debug("list_vars from '%s'...", ups)

        self._srv_handler.write("LIST RW %s\n" % ups)
        result = self._srv_handler.read_until("\n")
        if result != "BEGIN LIST RW %s\n" % ups:
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until("END LIST RW %s\n" % ups)
        offset = len("VAR %s" % ups)
        end_offset = 0 - (len("END LIST RW %s\n" % ups) + 1)
        rw_vars = {}

        try:
            for current in result[:end_offset].split("\n"):
                var = current[offset:].split('"')[0].replace(" ", "")
                data = current[offset:].split('"')[1]
                rw_vars[var] = data
        except Exception:
            # FIXME: Make this except more specific.
            pass

        return rw_vars

    def set_var(self, ups="", var="", value=""):
        """Set a variable to the specified value on selected UPS.

        The variable must be a writable value (cf list_rw_vars) and you
        must have the proper rights to set it (maybe login/password).
        """

        self._srv_handler.write("SET VAR %s %s %s\n" % (ups, var, value))
        result = self._srv_handler.read_until("\n")
        if result == "OK\n":
            return "OK"
        else:
            raise PyNUTError(result)

    def run_command(self, ups="", command=""):
        """Send a command to the specified UPS.

        Returns OK on success or raises an error.
        """

        logging.debug("run_command called...")

        self._srv_handler.write("INSTCMD %s %s\n" % (ups, command))
        result = self._srv_handler.read_until("\n")
        if result == "OK\n":
            return "OK"
        else:
            raise PyNUTError(result.replace("\n", ""))

    def fsd(self, ups=""):
        """Send FSD command.

        Returns OK on success or raises an error.
        """

        logging.debug("MASTER called...")

        self._srv_handler.write("MASTER %s\n" % ups)
        result = self._srv_handler.read_until("\n")
        if result != "OK MASTER-GRANTED\n":
            raise PyNUTError(("Master level function are not available", ""))

        logging.debug("FSD called...")
        self._srv_handler.write("FSD %s\n" % ups)
        result = self._srv_handler.read_until("\n")
        if result == "OK FSD-SET\n":
            return "OK"
        else:
            raise PyNUTError(result.replace("\n", ""))

    def help(self):
        """Send HELP command."""

        logging.debug("HELP called...")

        self._srv_handler.write("HELP\n")
        return self._srv_handler.read_until("\n")

    def ver(self):
        """Send VER command."""

        logging.debug("VER called...")

        self._srv_handler.write("VER\n")
        return self._srv_handler.read_until("\n")
