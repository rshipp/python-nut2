"""A simple mock NUT server for testing the Python client."""

class MockServer(object):
    def __init__(self, host=None, port=None, broken=True, ok=True,
            broken_username=False):
        self.valid = "test"
        self.broken = broken
        self.ok = ok
        self.broken_username = broken_username

    def write(self, text):
        self.command = text
        self.first = True

    def read_until(self, text=None, timeout=None):
        return self.run_command().split(text)[0] + text

    def close(self):
        pass

    def run_command(self):
        if self.broken and not self.broken_username and self.command == "USERNAME %s\n" % self.valid:
            return 'OK\n'
        elif self.broken:
            return 'ERR\n'
        elif self.command == "HELP\n":
            return 'Commands: HELP VER GET LIST SET INSTCMD LOGIN LOGOUT USERNAME PASSWORD STARTTLS\n'
        elif self.command == "VER\n":
            return 'Network UPS Tools upsd 2.7.1 - http://www.networkupstools.org/\n'
        elif self.command == "GET CMDDESC %s %s\n" % (self.valid, self.valid):
            return 'CMDDESC '+self.valid+' '+self.valid+' "Test description"\n'
        elif self.command == "LIST UPS\n" and self.first:
            self.first = False
            return 'BEGIN LIST UPS\n'
        elif self.command == "LIST UPS\n":
            return 'UPS '+self.valid+'"Test UPS 1"\nUPS Test_UPS2 "Test UPS 2"\nEND LIST UPS\n'
        elif self.command == "LIST VAR %s\n" % self.valid and self.first:
            self.first = False
            return 'BEGIN LIST VAR '+self.valid+'\n'
        elif self.command == "LIST VAR %s\n" % self.valid:
            return 'VAR '+self.valid+' battery.charge "100"\nVAR '+self.valid+' battery.voltage "14.44"\nEND LIST VAR '+self.valid+'\n'
        elif self.command.startswith("LIST VAR"):
            return 'ERR INVALID-ARGUMENT\n'
        elif self.command == "LIST CMD %s\n" % self.valid and self.first:
            self.first = False
            return 'BEGIN LIST CMD '+self.valid+'\n'
        elif self.command == "LIST CMD %s\n" % self.valid:
            return 'CMD '+self.valid+' '+self.valid+'\nEND LIST CMD '+self.valid+'\n'
        elif self.command.startswith("LIST CMD"):
            return 'ERR INVALID-ARGUMENT\n'
        elif self.command == "LIST RW %s\n" % self.valid and self.first:
            self.first = False
            return 'BEGIN LIST RW '+self.valid+'\n'
        elif self.command == "LIST RW %s\n" % self.valid:
            return 'RW '+self.valid+' '+self.valid+' "test"\nEND LIST RW '+self.valid+'\n'
        elif self.command.startswith("LIST RW"):
            return 'ERR INVALID-ARGUMENT\n'
        elif self.command == "LIST CLIENTS %s\n" % self.valid and self.first:
            self.first = False
            return 'BEGIN LIST CLIENTS\n'
        elif self.command == "LIST CLIENTS %s\n" % self.valid:
            return 'CLIENT '+self.valid+' '+self.valid+'\nEND LIST CLIENTS\n'
        elif self.command.startswith("LIST CLIENTS"):
            return 'ERR INVALID-ARGUMENT\n'
        # TODO: SET commands
        elif self.command == "SET VAR %s %s %s\n" % (self.valid, self.valid, self.valid):
            return 'OK\n'
        elif self.command.startswith("SET"):
            return 'ERR ACCESS-DENIED\n'
        elif self.command == "INSTCMD %s %s\n"% (self.valid, self.valid):
            return 'OK\n'
        elif self.command.startswith("INSTCMD"):
            return 'ERR CMD-NOT-SUPPORTED\n'
        # TODO: LOGIN/LOGOUT commands
        elif self.command == "USERNAME %s\n" % self.valid:
            return 'OK\n'
        elif self.command.startswith("USERNAME"):
            return 'OK\n'  # FIXME
        elif self.command == "PASSWORD %s\n" % self.valid:
            return 'OK\n'
        elif self.command.startswith("PASSWORD"):
            return 'OK\n'  # FIXME
        elif self.command == "STARTTLS\n":
            return 'ERR FEATURE-NOT-CONFIGURED\n'
        elif self.command == "MASTER %s\n" % self.valid:
            return 'OK MASTER-GRANTED\n'
        elif self.command == "FSD %s\n" % self.valid and self.ok:
            return 'OK FSD-SET\n'
        elif self.command == "FSD %s\n" % self.valid:
            return 'ERR\n'
        else:
            return 'ERR UNKNOWN-COMMAND\n'
