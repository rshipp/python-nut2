import unittest
from mockserver import MockServer
from nut2 import PyNUTClient

class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = PyNUTClient(connect=False, debug=True)
        self.client._srv_handler = MockServer()
        self.broken_client = PyNUTClient(connect=False, debug=True)
        self.broken_client._srv_handler = MockServer(broken=True)
        self.not_ok_client = PyNUTClient(connect=False, debug=True)
        self.not_ok_client._srv_handler = MockServer(ok=False)
        self.valid = "test"
        self.invalid = "does_not_exist"
        self.valid_ups_name = "Test UPS 1"
        self.valid_command_desc = "Test description"

    def test_init_with_args(self):
        PyNUTClient(connect=False, login='test', password='test',
                host='test', port=1)

    def test_get_ups_list(self):
        ups_list = self.client.GetUPSList()
        self.assertEquals(type(ups_list), dict)
        self.assertEquals(len(ups_list), 2)
        self.assertEquals(ups_list[self.valid], self.valid_ups_name)

    def test_get_ups_list_broken(self):
        self.assertRaises(Exception, self.broken_client.GetUPSList)

    def test_get_ups_vars_valid_ups(self):
        vars = self.client.GetUPSVars(self.valid)
        self.assertEquals(type(vars), dict)
        self.assertEquals(len(vars), 2)
        self.assertEquals(vars['battery.charge'], '100')

    def test_get_ups_vars_invalid_ups(self):
        self.assertRaises(Exception, self.client.GetUPSVars, self.invalid)

    def test_get_ups_vars_broken(self):
        self.assertRaises(Exception, self.broken_client.GetUPSVars, self.valid)

    def test_get_ups_commands_valid_ups(self):
        commands = self.client.GetUPSCommands(self.valid)
        self.assertEquals(type(commands), dict)
        self.assertEquals(len(commands), 1)
        self.assertEquals(commands[self.valid], self.valid_command_desc)

    def test_get_ups_commands_invalid_ups(self):
        self.assertRaises(Exception, self.client.GetUPSCommands, self.invalid)

    def test_get_ups_commands_broken(self):
        self.assertRaises(Exception, self.broken_client.GetUPSCommands,
                self.valid)

    def test_get_rw_vars_valid_ups(self):
        vars = self.client.GetRWVars(self.valid)
        self.assertEquals(type(vars), dict)
        self.assertEquals(vars[self.valid], self.valid)

    def test_get_rw_vars_invalid_ups(self):
        self.assertRaises(Exception, self.client.GetRWVars, self.invalid)

    def test_set_rw_var_valid(self):
        self.assertEquals(self.client.SetRWVar(self.valid, self.valid,
                    self.valid), 'OK')

    def test_set_rw_var_invalid(self):
        self.assertRaises(Exception, self.client.SetRWVar, self.invalid,
                self.invalid, self.invalid)

    def test_set_rw_var_broken(self):
        self.assertRaises(Exception, self.broken_client.SetRWVar, self.valid,
                self.valid, self.valid)

    def test_run_ups_command_valid(self):
        self.assertEquals(self.client.RunUPSCommand(self.valid,
                    self.valid), 'OK')

    def test_run_ups_command_invalid(self):
        self.assertRaises(Exception, self.client.RunUPSCommand, self.invalid,
                    self.invalid)

    def test_run_ups_command_broken(self):
        self.assertRaises(Exception, self.broken_client.RunUPSCommand, self.valid,
                    self.valid)

    def test_fsd_valid_ups(self):
        self.assertEquals(self.client.FSD(self.valid), 'OK')

    def test_fsd_invalid_ups(self):
        self.assertRaises(Exception, self.client.FSD, self.invalid)

    def test_fsd_broken(self):
        self.assertRaises(Exception, self.broken_client.FSD, self.valid)

    def test_fsd_not_ok(self):
        self.assertRaises(Exception, self.not_ok_client.FSD, self.valid)

    def test_help(self):
        self.assertEquals(self.client.help(), 'Commands: HELP VER GET LIST SET INSTCMD LOGIN LOGOUT USERNAME PASSWORD STARTTLS\n')

    def test_ver(self):
        self.assertEquals(self.client.ver(), 'Network UPS Tools upsd 2.7.1 - http://www.networkupstools.org/\n')

    def test_list_clients_valid(self):
        clients = self.client.ListClients(self.valid)
        self.assertEquals(type(clients), dict)
        self.assertEquals(clients[self.valid], [self.valid])

    def test_list_clients_invalid(self):
        self.assertRaises(Exception, self.client.ListClients,
                self.invalid)

    def test_list_clients_none(self):
        self.assertRaises(Exception, self.client.ListClients)

    def test_list_clients_broken(self):
        self.assertRaises(Exception, self.broken_client.ListClients,
                self.valid)
