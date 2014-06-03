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


__version__ = '2.0.0'
__all__ = ['PyNUTError', 'PyNUTClient']


class PyNUTError(Exception):
    """Base class for custom exceptions."""

class PyNUTClient(object):
    """Access NUT (Network UPS Tools) servers."""

    def __init__(self, host="127.0.0.1", port=3493, login=None, password=None, debug=False, timeout=5, connect=True):
        """Class initialization method.

        host     : Host to connect (defaults to 127.0.0.1)
        port     : Port where NUT listens for connections (defaults to 3493)
        login    : Login used to connect to NUT server (defaults to None
                   for no authentication)
        password : Password used when using authentication (defaults to None)
        debug    : Boolean, put class in debug mode (prints everything
                   on console, default to False)
        timeout  : Timeout used to wait for network response
        """
        self._debug = debug

        if self._debug:
            print("[DEBUG] Class initialization...")
            print("[DEBUG]  -> Host = %s (port %s)" % (host, port))
            print("[DEBUG]  -> Login = '%s' / '%s'" % (login, password))

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

    def _connect(self):
        """Connects to the defined server.

        If login/pass was specified, the class tries to authenticate.
        An error is raised if something goes wrong.
        """
        if self._debug:
            print("[DEBUG] Connecting to host")

        self._srv_handler = telnetlib.Telnet(self._host, self._port)

        if self._login != None:
            self._srv_handler.write("USERNAME %s\n" % self._login)
            result = self._srv_handler.read_until("\n", self._timeout)
            if result[:2] != "OK":
                raise PyNUTError(result.replace("\n", ""))

        if self._password != None:
            self._srv_handler.write("PASSWORD %s\n" % self._password)
            result = self._srv_handler.read_until("\n", self._timeout)
            if result[:2] != "OK":
                raise PyNUTError(result.replace("\n", ""))

    def list_ups(self):
        """Returns the list of available UPS from the NUT server.

        The result is a dictionary containing 'key->val' pairs of
        'UPSName' and 'UPS Description'.
        """
        if self._debug:
            print("[DEBUG] list_ups from server")

        self._srv_handler.write("LIST UPS\n")
        result = self._srv_handler.read_until("\n")
        if result != "BEGIN LIST UPS\n":
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until("END LIST UPS\n")
        ups_dict = {}

        for line in result.split("\n"):
            if line[:3] == "UPS":
                ups, desc = line[4:-1].split('"')
                ups_dict[ups.replace(" ", "")] = desc

        return ups_dict

    def list_vars(self, ups=""):
        """Get all available vars from the specified UPS.

        The result is a dictionary containing 'key->val' pairs of all
        available vars.
        """
        if self._debug:
            print("[DEBUG] list_vars called...")

        self._srv_handler.write("LIST VAR %s\n" % ups)
        result = self._srv_handler.read_until("\n")
        if result != "BEGIN LIST VAR %s\n" % ups:
            raise PyNUTError(result.replace("\n", ""))

        ups_vars = {}
        result = self._srv_handler.read_until("END LIST VAR %s\n" % ups)
        offset = len("VAR %s " % ups)
        end_offset = 0 - (len("END LIST VAR %s\n" % ups) + 1)

        for current in result[:end_offset].split("\n"):
            var = current[offset:].split('"')[0].replace(" ", "")
            data = current[offset:].split('"')[1]
            ups_vars[var] = data

        return ups_vars

    def list_commands(self, ups=""):
        """Get all available commands for the specified UPS.

        The result is a dict object with command name as key and a description
        of the command as value.
        """
        if self._debug:
            print("[DEBUG] list_commands called...")

        self._srv_handler.write("LIST CMD %s\n" % ups)
        result = self._srv_handler.read_until("\n")
        if result != "BEGIN LIST CMD %s\n" % ups:
            raise PyNUTError(result.replace("\n", ""))

        ups_cmds = {}
        result = self._srv_handler.read_until("END LIST CMD %s\n" % ups)
        offset = len("CMD %s " % ups)
        end_offset = 0 - (len("END LIST CMD %s\n" % ups) + 1)

        for current in result[:end_offset].split("\n"):
            var = current[offset:].split('"')[0].replace(" ", "")

            # For each var we try to get the available description
            try:
                self._srv_handler.write("GET CMDDESC %s %s\n" % (ups, var))
                temp = self._srv_handler.read_until("\n")
                if temp[:7] != "CMDDESC":
                    raise PyNUTError
                else:
                    off = len("CMDDESC %s %s " % (ups, var))
                    desc = temp[off:-1].split('"')[1]
            except PyNUTError:
                desc = var

            ups_cmds[var] = desc

        return ups_cmds

    def list_clients(self, ups=None):
        """Returns the list of connected clients from the NUT server.

        The result is a dictionary containing 'key->val' pairs of
        'UPSName' and a list of clients.
        """
        if self._debug:
            print("[DEBUG] list_clients from server")

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
        ups_dict = {}

        for line in result.split("\n"):
            if line[:6] == "CLIENT":
                host, ups = line[7:].split(' ')
                ups.replace(' ', '')
                if not ups in ups_dict:
                    ups_dict[ups] = []
                ups_dict[ups].append(host)

        return ups_dict

    def list_rw_vars(self, ups=""):
        """Get a list of all writable vars from the selected UPS.

        The result is presented as a dictionary containing 'key->val'
        pairs.
        """
        if self._debug:
            print("[DEBUG] list_vars from '%s'..." % ups)

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

        if self._debug:
            print("[DEBUG] run_command called...")

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

        if self._debug:
            print("[DEBUG] MASTER called...")

        self._srv_handler.write("MASTER %s\n" % ups)
        result = self._srv_handler.read_until("\n")
        if result != "OK MASTER-GRANTED\n":
            raise PyNUTError(("Master level function are not available", ""))

        if self._debug:
            print("[DEBUG] FSD called...")
        self._srv_handler.write("FSD %s\n" % ups)
        result = self._srv_handler.read_until("\n")
        if result == "OK FSD-SET\n":
            return "OK"
        else:
            raise PyNUTError(result.replace("\n", ""))

    def help(self):
        """Send HELP command."""

        if self._debug:
            print("[DEBUG] HELP called...")

        self._srv_handler.write("HELP\n")
        return self._srv_handler.read_until("\n")

    def ver(self):
        """Send VER command."""

        if self._debug:
            print("[DEBUG] VER called...")

        self._srv_handler.write("VER\n")
        return self._srv_handler.read_until("\n")
