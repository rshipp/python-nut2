"""A simple mock NUT server for testing the Python client."""

class MockServer(object):
    def __init__(self, host=None, port=None, broken=True, ok=True,
            broken_username=False, timeout=None):
        self.valid = b"test"
        self.valid_desc = b'"Test UPS 1"'
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
        if self.broken and not self.broken_username and self.command == b"USERNAME %s\n" % self.valid:
            return b'OK\n'
        elif self.broken:
            return b'ERR\n'
        elif self.command == b"HELP\n":
            return b'Commands: HELP VER GET LIST SET INSTCMD LOGIN LOGOUT USERNAME PASSWORD STARTTLS\n'
        elif self.command == b"VER\n":
            return b'Network UPS Tools upsd 2.7.1 - http://www.networkupstools.org/\n'
        elif self.command == b"GET CMDDESC %s %s\n" % (self.valid, self.valid):
            return b'CMDDESC '+self.valid+b' '+self.valid+b' '+self.valid_desc+b'\n'
        elif self.command == b"LIST UPS\n" and self.first:
            self.first = False
            return b'BEGIN LIST UPS\n'
        elif self.command == b"LIST UPS\n":
            return b'UPS '+self.valid+b' '+self.valid_desc+b'\nUPS Test_UPS2 "Test UPS 2"\nEND LIST UPS\n'
        elif self.command == b"LIST VAR %s\n" % self.valid and self.first:
            self.first = False
            return b'BEGIN LIST VAR '+self.valid+b'\n'
        elif self.command == b"LIST VAR %s\n" % self.valid:
            return b'VAR '+self.valid+b' battery.charge "100"\nVAR '+self.valid+b' battery.voltage "14.44"\nEND LIST VAR '+self.valid+b'\n'
        elif self.command.startswith(b"LIST VAR"):
            return b'ERR INVALID-ARGUMENT\n'
        elif self.command == b"LIST CMD %s\n" % self.valid and self.first:
            self.first = False
            return b'BEGIN LIST CMD '+self.valid+b'\n'
        elif self.command == b"LIST CMD %s\n" % self.valid:
            return b'CMD '+self.valid+b' '+self.valid+b'\nEND LIST CMD '+self.valid+b'\n'
        elif self.command.startswith(b"LIST CMD"):
            return b'ERR INVALID-ARGUMENT\n'
        elif self.command == b"LIST RW %s\n" % self.valid and self.first:
            self.first = False
            return b'BEGIN LIST RW '+self.valid+b'\n'
        elif self.command == b"LIST RW %s\n" % self.valid:
            return b'RW '+self.valid+b' '+self.valid+b' "test"\nEND LIST RW '+self.valid+b'\n'
        elif self.command.startswith(b"LIST RW"):
            return b'ERR INVALID-ARGUMENT\n'
        elif self.command == b"LIST CLIENTS %s\n" % self.valid and self.first:
            self.first = False
            return b'BEGIN LIST CLIENTS\n'
        elif self.command == b"LIST CLIENTS %s\n" % self.valid:
            return b'CLIENT '+self.valid+b' '+self.valid+b'\nEND LIST CLIENTS\n'
        elif self.command.startswith(b"LIST CLIENTS"):
            return b'ERR INVALID-ARGUMENT\n'
        elif self.command == b"LIST ENUM %s %s\n" % (self.valid, self.valid) and self.first:
            self.first = False
            return b'BEGIN LIST ENUM %s %s\n' % (self.valid, self.valid)
        elif self.command == b"LIST ENUM %s %s\n" % (self.valid, self.valid):
            return b'ENUM %s %s %s\nEND LIST ENUM %s %s\n' % (self.valid,
                    self.valid, self.valid_desc, self.valid, self.valid)
        elif self.command == b"LIST RANGE %s %s\n" % (self.valid, self.valid) and self.first:
            self.first = False
            return b'BEGIN LIST RANGE %s %s\n' % (self.valid, self.valid)
        elif self.command == b"LIST RANGE %s %s\n" % (self.valid, self.valid):
            return b'RANGE %s %s %s %s\nEND LIST RANGE %s %s\n' % (self.valid,
                    self.valid, self.valid_desc, self.valid_desc, self.valid, self.valid)
        elif self.command == b"SET VAR %s %s %s\n" % (self.valid, self.valid, self.valid):
            return b'OK\n'
        elif self.command.startswith(b"SET"):
            return b'ERR ACCESS-DENIED\n'
        elif self.command == b"INSTCMD %s %s\n"% (self.valid, self.valid):
            return b'OK\n'
        elif self.command.startswith(b"INSTCMD"):
            return b'ERR CMD-NOT-SUPPORTED\n'
        # TODO: LOGIN/LOGOUT commands
        elif self.command == b"USERNAME %s\n" % self.valid:
            return b'OK\n'
        elif self.command.startswith(b"USERNAME"):
            return b'ERR\n'  # FIXME: What does it say on invalid password?
        elif self.command == b"PASSWORD %s\n" % self.valid:
            return b'OK\n'
        elif self.command.startswith(b"PASSWORD"):
            return b'ERR\n'  # FIXME: ^
        elif self.command == b"STARTTLS\n":
            return b'ERR FEATURE-NOT-CONFIGURED\n'
        elif self.command == b"MASTER %s\n" % self.valid:
            return b'OK MASTER-GRANTED\n'
        elif self.command == b"FSD %s\n" % self.valid and self.ok:
            return b'OK FSD-SET\n'
        elif self.command == b"FSD %s\n" % self.valid:
            return b'ERR\n'
        elif self.command == b"GET NUMLOGINS %s\n" % self.valid:
            return b'NUMLOGINS %s 1\n' % self.valid
        elif self.command.startswith(b"GET NUMLOGINS"):
            return b'ERR UNKNOWN-UPS\n'
        elif self.command == b"GET UPSDESC %s\n" % self.valid:
            return b'UPSDESC %s %s\n' % (self.valid, self.valid_desc)
        elif self.command.startswith(b"GET UPSDESC"):
            return b'ERR UNKNOWN-UPS\n'
        elif self.command == b"GET VAR %s %s\n" % (self.valid, self.valid):
            return b'VAR %s %s "100"\n' % (self.valid, self.valid)
        elif self.command.startswith(b"GET VAR %s" % self.valid):
            return b'ERR VAR-NOT-SUPPORTED\n'
        elif self.command.startswith(b"GET VAR "):
            return b'ERR UNKNOWN-UPS\n'
        elif self.command.startswith(b"GET VAR"):
            return b'ERR INVALID-ARGUMENT\n'
        elif self.command == b"GET TYPE %s %s\n" % (self.valid, self.valid):
            return b'TYPE %s %s RW STRING:3\n' % (self.valid, self.valid)
        elif self.command.startswith(b"GET TYPE %s" % self.valid):
            return b'ERR VAR-NOT-SUPPORTED\n'
        elif self.command.startswith(b"GET TYPE"):
            return b'ERR INVALID-ARGUMENT\n'
        elif self.command == b"GET DESC %s %s\n" % (self.valid, self.valid):
            return b'DESC %s %s %s\n' % (self.valid, self.valid, self.valid_desc)
        elif self.command.startswith(b"GET DESC"):
            return b'ERR-INVALID-ARGUMENT\n'
        elif self.command == b"GET CMDDESC %s %s" % (self.valid, self.valid):
            return b'CMDDESC %s %s %s\n' % (self.valid, self.valid, self.valid_desc)
        elif self.command.startswith(b"GET CMDDESC"):
            return b'ERR INVALID-ARGUMENT'
        else:
            return b'ERR UNKNOWN-COMMAND\n'
