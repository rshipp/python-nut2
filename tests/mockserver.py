"""A simple mock NUT server for testing the Python client."""

class MockServer(object):
    def __init__(self, host=None, port=None, broken=True, ok=True,
            broken_username=False, timeout=None):
        self.valid = "test"
        self.valid_desc = '"Test UPS 1"'
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
            return 'CMDDESC '+self.valid+' '+self.valid+' '+self.valid_desc+'\n'
        elif self.command == "LIST UPS\n" and self.first:
            self.first = False
            return 'BEGIN LIST UPS\n'
        elif self.command == "LIST UPS\n":
            return 'UPS '+self.valid+' '+self.valid_desc+'\nUPS Test_UPS2 "Test UPS 2"\nEND LIST UPS\n'
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
        elif self.command == "LIST ENUM %s %s\n" % (self.valid, self.valid) and self.first:
            self.first = False
            return 'BEGIN LIST ENUM %s %s\n' % (self.valid, self.valid)
        elif self.command == "LIST ENUM %s %s\n" % (self.valid, self.valid):
            return 'ENUM %s %s %s\nEND LIST ENUM %s %s\n' % (self.valid,
                    self.valid, self.valid_desc, self.valid, self.valid)
        elif self.command == "LIST RANGE %s %s\n" % (self.valid, self.valid) and self.first:
            self.first = False
            return 'BEGIN LIST RANGE %s %s\n' % (self.valid, self.valid)
        elif self.command == "LIST RANGE %s %s\n" % (self.valid, self.valid):
            return 'RANGE %s %s %s %s\nEND LIST RANGE %s %s\n' % (self.valid,
                    self.valid, self.valid_desc, self.valid_desc, self.valid, self.valid)
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
            return 'ERR\n'  # FIXME: What does it say on invalid password?
        elif self.command == "PASSWORD %s\n" % self.valid:
            return 'OK\n'
        elif self.command.startswith("PASSWORD"):
            return 'ERR\n'  # FIXME: ^
        elif self.command == "STARTTLS\n":
            return 'ERR FEATURE-NOT-CONFIGURED\n'
        elif self.command == "MASTER %s\n" % self.valid:
            return 'OK MASTER-GRANTED\n'
        elif self.command == "FSD %s\n" % self.valid and self.ok:
            return 'OK FSD-SET\n'
        elif self.command == "FSD %s\n" % self.valid:
            return 'ERR\n'
        elif self.command == "GET NUMLOGINS %s\n" % self.valid:
            return 'NUMLOGINS %s 1\n' % self.valid
        elif self.command.startswith("GET NUMLOGINS"):
            return 'ERR UNKNOWN-UPS\n'
        elif self.command == "GET UPSDESC %s\n" % self.valid:
            return 'UPSDESC %s %s\n' % (self.valid, self.valid_desc)
        elif self.command.startswith("GET UPSDESC"):
            return 'ERR UNKNOWN-UPS\n'
        elif self.command == "GET VAR %s %s\n" % (self.valid, self.valid):
            return 'VAR %s %s "100"\n' % (self.valid, self.valid)
        elif self.command.startswith("GET VAR %s" % self.valid):
            return 'ERR VAR-NOT-SUPPORTED\n'
        elif self.command.startswith("GET VAR "):
            return 'ERR UNKNOWN-UPS\n'
        elif self.command.startswith("GET VAR"):
            return 'ERR INVALID-ARGUMENT\n'
        elif self.command == "GET TYPE %s %s\n" % (self.valid, self.valid):
            return 'TYPE %s %s RW STRING:3\n' % (self.valid, self.valid)
        elif self.command.startswith("GET TYPE %s" % self.valid):
            return 'ERR VAR-NOT-SUPPORTED\n'
        elif self.command.startswith("GET TYPE"):
            return 'ERR INVALID-ARGUMENT\n'
        elif self.command == "GET DESC %s %s\n" % (self.valid, self.valid):
            return 'DESC %s %s %s\n' % (self.valid, self.valid, self.valid_desc)
        elif self.command.startswith("GET DESC"):
            return 'ERR-INVALID-ARGUMENT\n'
        elif self.command == "GET CMDDESC %s %s" % (self.valid, self.valid):
            return 'CMDDESC %s %s %s\n' % (self.valid, self.valid, self.valid_desc)
        elif self.command.startswith("GET CMDDESC"):
            return 'ERR INVALID-ARGUMENT'
        else:
            return 'ERR UNKNOWN-COMMAND\n'
