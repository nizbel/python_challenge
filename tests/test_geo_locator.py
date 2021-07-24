import unittest
from unittest.mock import patch, mock_open

import requests

from geo_locator import GeoLocator


class GeoLocatorTestCase(unittest.TestCase):
    empty_cache = '[]'
    filled_cache = '[{"ip": "40.82.106.5", "country": "Switzerland", "country_code": "CH", "region": "ZH", ' \
                   '"region_name": "Zurich", "city": "Zurich", "zip_code": "8045", "timezone": "Europe/Zurich", ' \
                   '"latitude": 47.3682, "longitude": 8.5671, "isp": "Microsoft Corporation"}, {"ip": ' \
                   '"81.44.150.240", "country": "Spain", "country_code": "ES", "region": "GA", "region_name": ' \
                   '"Galicia", "city": "Santiago de Compostela", "zip_code": "15701", "timezone": "Europe/Madrid", ' \
                   '"latitude": 42.8769, "longitude": -8.5471, "isp": "Telefonica de Espana SAU"}, {"ip": ' \
                   '"244.36.171.60", "error_message": "reserved range"}]'

    @patch('builtins.open', mock_open(read_data=empty_cache))
    def test_init_empty(self):
        geo_locator = GeoLocator()
        self.assertTrue(len(geo_locator.ips_list) == 0)

    @patch('builtins.open', mock_open(read_data=empty_cache))
    def test_init_filled(self):
        geo_locator = GeoLocator(['40.82.106.5', '81.44.150.240'])
        self.assertTrue(len(geo_locator.ips_list) == 2)

    @patch('builtins.open', mock_open(read_data=empty_cache))
    def test_set_list(self):
        geo_locator = GeoLocator()
        geo_locator.set_ip_list(['40.82.106.5', '81.44.150.240'])

        # Should update ip list
        self.assertEqual('40.82.106.5', geo_locator.ips_list[0])
        self.assertEqual('81.44.150.240', geo_locator.ips_list[1])

        # Should reset geo location list index
        self.assertEqual(0, geo_locator.cur_geo_info_index)

    @patch('builtins.open', mock_open(read_data=empty_cache))
    def test_load_cache_empty(self):
        geo_locator = GeoLocator()
        self.assertEqual({}, geo_locator.cache)

    @patch('builtins.open', mock_open(read_data=filled_cache))
    def test_load_cache_filled(self):
        geo_locator = GeoLocator()
        self.assertEqual(3, len(geo_locator.cache.keys()))
        self.assertIn('40.82.106.5', geo_locator.cache.keys())
        self.assertIn('81.44.150.240', geo_locator.cache.keys())
        self.assertIn('244.36.171.60', geo_locator.cache.keys())

    @patch('builtins.open', mock_open(read_data=empty_cache))
    def test_prepare_request_data_empty_cache(self):
        geo_locator = GeoLocator(['40.82.106.5', '81.44.150.240'])
        geo_locator.prepare_request_data()

        # Should have both ips in request data
        self.assertIn('40.82.106.5', geo_locator.request_data)
        self.assertIn('81.44.150.240', geo_locator.request_data)

if __name__ == '__main__':
    unittest.main()
