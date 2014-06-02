import unittest

from nut2 import PyNUTClient

class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = PyNUTClient()

    def test_get_ups_list(self):
        self.client.GetUPSList()
