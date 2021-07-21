import unittest
import requests

from parser import *


class ParserTestCase(unittest.TestCase):
    def test_check_valid_ip(self):
        self.assertTrue(is_valid_ip('172.0.0.1'))

    def test_check_invalid_ip(self):
        self.assertFalse(is_valid_ip('256.255.255.0'))

    def test_parse_ip_from_text(self):
        parser = IPParser()
        ips = parser.parse('192.168.0.1lorem ipsum')
        self.assertEqual(len(ips), 1)
        self.assertEqual('192.168.0.1', ips[0])


if __name__ == '__main__':
    unittest.main()
