# -*- coding: utf-8 -*-

"""A Python module for dealing with NUT (Network UPS Tools) servers.

* PyNUTError: Base class for custom exceptions.
* PyNUTClient: Allows connecting to and communicating with PyNUT
  servers.

Copyright (C) 2019 Ryan Shipp

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import telnetlib
import logging


__version__ = '2.1.1'
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
                self._srv_handler.write(b"LOGOUT\n")
                self._srv_handler.close()
            except (telnetlib.socket.error, AttributeError):
                # The socket is already disconnected.
                pass

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

        try:
            self._srv_handler = telnetlib.Telnet(self._host, self._port,
                                                 timeout=self._timeout)

            if self._login is not None:
                self._srv_handler.write(b"USERNAME %s\n" % self._login.encode('utf-8'))
                result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
                if not result == "OK\n":
                    raise PyNUTError(result.replace("\n", ""))

            if self._password is not None:
                self._srv_handler.write(b"PASSWORD %s\n" % self._password.encode('utf-8'))
                result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
                if not result == "OK\n":
                    raise PyNUTError(result.replace("\n", ""))
        except telnetlib.socket.error:
            raise PyNUTError("Socket error.")

    def description(self, ups):
        """Returns the description for a given UPS."""
        logging.debug("description called...")

        self._srv_handler.write(b"GET UPSDESC %s\n" % ups.encode('utf-8'))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        try:
            return result.split('"')[1].strip()
        except IndexError:
            raise PyNUTError(result.replace("\n", ""))

    def list_ups(self):
        """Returns the list of available UPS from the NUT server.

        The result is a dictionary containing 'key->val' pairs of
        'UPSName' and 'UPS Description'.
        """
        logging.debug("list_ups from server")

        self._srv_handler.write(b"LIST UPS\n")
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "BEGIN LIST UPS\n":
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until(b"END LIST UPS\n",
                                              self._timeout).decode('utf-8')

        ups_dict = {}
        for line in result.split("\n"):
            if line.startswith("UPS"):
                ups, desc = line[len("UPS "):-len('"')].split('"')[:2]
                ups_dict[ups.strip()] = desc.strip()

        return ups_dict

    def list_vars(self, ups):
        """Get all available vars from the specified UPS.

        The result is a dictionary containing 'key->val' pairs of all
        available vars.
        """
        logging.debug("list_vars called...")

        self._srv_handler.write(b"LIST VAR %s\n" % ups.encode('utf-8'))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "BEGIN LIST VAR %s\n" % ups:
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until(b"END LIST VAR %s\n" % ups.encode('utf-8'),
                                              self._timeout).decode('utf-8')
        offset = len("VAR %s " % ups)
        end_offset = 0 - (len("END LIST VAR %s\n" % ups) + 1)

        ups_vars = {}
        for current in result[:end_offset].split("\n"):
            var, data = current[offset:].split('"')[:2]
            ups_vars[var.strip()] = data

        return ups_vars

    def list_commands(self, ups):
        """Get all available commands for the specified UPS.

        The result is a dict object with command name as key and a description
        of the command as value.
        """
        logging.debug("list_commands called...")

        self._srv_handler.write(b"LIST CMD %s\n" % ups.encode('utf-8'))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "BEGIN LIST CMD %s\n" % ups:
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until(b"END LIST CMD %s\n" % ups.encode('utf-8'),
                                              self._timeout).decode('utf-8')
        offset = len("CMD %s " % ups)
        end_offset = 0 - (len("END LIST CMD %s\n" % ups) + 1)

        commands = {}
        for current in result[:end_offset].split("\n"):
            command = current[offset:].split('"')[0].strip()

            # For each var we try to get the available description
            try:
                self._srv_handler.write(b"GET CMDDESC %s %s\n" % (ups.encode('utf-8'), command.encode('utf-8')))
                temp = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
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
            self._srv_handler.write(b"LIST CLIENTS %s\n" % ups.encode('utf-8'))
        else:
            self._srv_handler.write(b"LIST CLIENTS\n")
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "BEGIN LIST CLIENTS\n":
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until(b"END LIST CLIENTS\n",
                                              self._timeout).decode('utf-8')

        clients = {}
        for line in result.split("\n"):
            if line.startswith("CLIENT"):
                host, ups = line[len("CLIENT "):].split(' ')[:2]
                if ups not in clients:
                    clients[ups] = []
                clients[ups].append(host)

        return clients

    def list_rw_vars(self, ups):
        """Get a list of all writable vars from the selected UPS.

        The result is presented as a dictionary containing 'key->val'
        pairs.
        """
        logging.debug("list_vars from '%s'...", ups)

        self._srv_handler.write(b"LIST RW %s\n" % ups.encode('utf-8'))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "BEGIN LIST RW %s\n" % ups:
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until(b"END LIST RW %s\n" % ups.encode('utf-8'),
                                              self._timeout).decode('utf-8')
        offset = len("VAR %s" % ups)
        end_offset = 0 - (len("END LIST RW %s\n" % ups) + 1)

        rw_vars = {}
        for current in result[:end_offset].split("\n"):
            var, data = current[offset:].split('"')[:2]
            rw_vars[var.strip()] = data

        return rw_vars

    def list_enum(self, ups, var):
        """Get a list of valid values for an enum variable.

        The result is presented as a list.
        """
        logging.debug("list_enum from '%s'...", ups)

        self._srv_handler.write(b"LIST ENUM %s %s\n" % (ups.encode('utf-8'), var.encode('utf-8')))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "BEGIN LIST ENUM %s %s\n" % (ups, var):
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until(b"END LIST ENUM %s %s\n" % (ups.encode('utf-8'), var.encode('utf-8')),
                                              self._timeout).decode('utf-8')
        offset = len("ENUM %s %s" % (ups, var))
        end_offset = 0 - (len("END LIST ENUM %s %s\n" % (ups, var)) + 1)

        try:
            return [ c[offset:].split('"')[1].strip() 
                     for c in result[:end_offset].split("\n") ]
        except IndexError:
            raise PyNUTError(result.replace("\n", ""))

    def list_range(self, ups, var):
        """Get a list of valid values for an range variable.

        The result is presented as a list.
        """
        logging.debug("list_range from '%s'...", ups)

        self._srv_handler.write(b"LIST RANGE %s %s\n" % (ups.encode('utf-8'), var.encode('utf-8')))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "BEGIN LIST RANGE %s %s\n" % (ups, var):
            raise PyNUTError(result.replace("\n", ""))

        result = self._srv_handler.read_until(b"END LIST RANGE %s %s\n" % (ups.encode('utf-8'), var.encode('utf-8')),
                                              self._timeout).decode('utf-8')
        offset = len("RANGE %s %s" % (ups, var))
        end_offset = 0 - (len("END LIST RANGE %s %s\n" % (ups, var)) + 1)

        try:
            return [ c[offset:].split('"')[1].strip() 
                     for c in result[:end_offset].split("\n") ]
        except IndexError:
            raise PyNUTError(result.replace("\n", ""))

    def set_var(self, ups, var, value):
        """Set a variable to the specified value on selected UPS.

        The variable must be a writable value (cf list_rw_vars) and you
        must have the proper rights to set it (maybe login/password).
        """
        logging.debug("set_var '%s' from '%s' to '%s'", var, ups, value)

        self._srv_handler.write(b"SET VAR %s %s %s\n" % (ups.encode('utf-8'), var.encode('utf-8'), value.encode('utf-8')))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "OK\n":
            raise PyNUTError(result.replace("\n", ""))

    def get_var(self, ups, var):
        """Get the value of a variable."""
        logging.debug("get_var called...")

        self._srv_handler.write(b"GET VAR %s %s\n" % (ups.encode('utf-8'), var.encode('utf-8')))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        try:
            # result = 'VAR %s %s "%s"\n' % (ups, var, value)
            return result.split('"')[1].strip()
        except IndexError:
            raise PyNUTError(result.replace("\n", ""))

    # Alias for convenience
    def get(self, ups, var):
        """Get the value of a variable (alias for get_var)."""
        return self.get_var(ups, var)

    def var_description(self, ups, var):
        """Get a variable's description."""
        logging.debug("var_description called...")

        self._srv_handler.write(b"GET DESC %s %s\n" % (ups.encode('utf-8'), var.encode('utf-8')))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        try:
            # result = 'DESC %s %s "%s"\n' % (ups, var, description)
            return result.split('"')[1].strip()
        except IndexError:
            raise PyNUTError(result.replace("\n", ""))

    def var_type(self, ups, var):
        """Get a variable's type."""
        logging.debug("var_type called...")

        self._srv_handler.write(b"GET TYPE %s %s\n" % (ups.encode('utf-8'), var.encode('utf-8')))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        try:
            # result = 'TYPE %s %s %s\n' % (ups, var, type)
            type_ = ' '.join(result.split(' ')[3:]).strip()
            # Ensure the response was valid.
            assert(len(type_) > 0)
            assert(result.startswith("TYPE"))
            return type_
        except AssertionError:
            raise PyNUTError(result.replace("\n", ""))

    def command_description(self, ups, command):
        """Get a command's description."""
        logging.debug("command_description called...")

        self._srv_handler.write(b"GET CMDDESC %s %s\n" % (ups.encode('utf-8'), command.encode('utf-8')))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        try:
            # result = 'CMDDESC %s %s "%s"' % (ups, command, description)
            return result.split('"')[1].strip()
        except IndexError:
            raise PyNUTError(result.replace("\n", ""))

    def run_command(self, ups, command):
        """Send a command to the specified UPS."""
        logging.debug("run_command called...")

        self._srv_handler.write(b"INSTCMD %s %s\n" % (ups.encode('utf-8'), command.encode('utf-8')))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "OK\n":
            raise PyNUTError(result.replace("\n", ""))

    def fsd(self, ups):
        """Send MASTER and FSD commands."""
        logging.debug("MASTER called...")

        self._srv_handler.write(b"MASTER %s\n" % ups.encode('utf-8'))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "OK MASTER-GRANTED\n":
            raise PyNUTError(("Master level function are not available", ""))

        logging.debug("FSD called...")
        self._srv_handler.write(b"FSD %s\n" % ups.encode('utf-8'))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        if result != "OK FSD-SET\n":
            raise PyNUTError(result.replace("\n", ""))

    def num_logins(self, ups):
        """Send GET NUMLOGINS command to get the number of users logged
        into a given UPS.
        """
        logging.debug("num_logins called on '%s'...", ups)

        self._srv_handler.write(b"GET NUMLOGINS %s\n" % ups.encode('utf-8'))
        result = self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
        try:
            # result = "NUMLOGINS %s %s\n" % (ups, int(numlogins))
            return int(result.split(' ')[2].strip())
        except (ValueError, IndexError):
            raise PyNUTError(result.replace("\n", ""))

    def help(self):
        """Send HELP command."""
        logging.debug("HELP called...")

        self._srv_handler.write(b"HELP\n")
        return self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')

    def ver(self):
        """Send VER command."""
        logging.debug("VER called...")

        self._srv_handler.write(b"VER\n")
        return self._srv_handler.read_until(b"\n", self._timeout).decode('utf-8')
