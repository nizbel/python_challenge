import json
import requests


class GeoInfo:
    def __init__(self, ip, country='', country_code='', region='', region_name='', city='', zip_code='',
                 timezone='', latitude='', longitude='', isp='', as_info='', error_message=''):
        self.ip = ip
        self.country = country
        self.country_code = country_code
        self.region = region
        self.region_name = region_name
        self.city = city
        self.zip_code = zip_code
        self.timezone = timezone
        self.latitude = latitude
        self.longitude = longitude
        self.isp = isp
        self.as_info = as_info
        self.error_message = error_message

    def fill_geo_info(self, country, country_code, region, region_name, city, zip_code,
                      timezone, latitude, longitude, isp, as_info):
        self.country = country
        self.country_code = country_code
        self.region = region
        self.region_name = region_name
        self.city = city
        self.zip_code = zip_code
        self.timezone = timezone
        self.latitude = latitude
        self.longitude = longitude
        self.isp = isp
        self.as_info = as_info

    def fill_error_message(self, error_message):
        self.error_message = error_message

    @staticmethod
    def to_json(obj):
        # return json.dumps(self, default=lambda o: o.__dict__,
        #                   sort_keys=True)
        if obj.error_message:
            return {'ip': obj.ip, 'error_message': obj.error_message}
        return {
            'ip': obj.ip,
            'country': obj.country,
            'country_code': obj.country_code,
            'region': obj.region,
            'region_name': obj.region_name,
            'city': obj.city,
            'zip_code': obj.zip_code,
            'timezone': obj.timezone,
            'latitude': obj.latitude,
            'longitude': obj.longitude,
            'isp': obj.isp
        }

    @staticmethod
    def decode_json(json_dict):
        return GeoInfo(**json_dict)


class GeoLocator:
    # url = 'http://ipinfo.io/
    # URL for a batch search of up to 100 ips
    url = 'http://ip-api.com/batch'

    cache_size = 10000
    cache_file = '.geocache'

    def __init__(self, ips_list=[]):
        self.ips_list = list(ips_list)
        self.request_data = []
        self.geo_info_list = []
        # Keeps track of the current index of the list we are getting info
        self.cur_geo_info_index = 0

        self.cache = {}
        self.load_cache()

    def load_cache(self):
        """
        Load cache from .cache file
        """
        try:
            with open(self.cache_file, 'r') as cache:
                geo_info_list = json.load(cache, object_hook=GeoInfo.decode_json)
                for geo_info in geo_info_list:
                    self.cache[geo_info.ip] = geo_info

        except FileNotFoundError:
            # Initialize cache file
            with open(self.cache_file, 'w') as cache:
                cache.write('[]')

    def set_ip_list(self, ips_list):
        """
        Sets a new IPs list
        :param ips_list: list of IPs as strings
        """
        self.ips_list = list(ips_list)
        self.cur_geo_info_index = 0

    def prepare_request_data(self):
        """
        Fills request data up to 100 IPs
        """
        self.request_data = []

        while len(self.request_data) < 100 and self.ips_list:
            ip = self.ips_list.pop()
            # Check for cached ips
            if ip in self.cache:
                self.geo_info_list.append(self.cache[ip])
            elif ip in self.request_data:
                # If ip is already in request data, avoid sending it
                self.geo_info_list.append(GeoInfo(ip))
            else:
                self.request_data.append(ip)
                self.geo_info_list.append(GeoInfo(ip))

    def update_cache(self):
        """
        Writes cache info to .cache file
        """
        with open(self.cache_file, 'w') as cache:
            cache_values = list(self.cache.values())
            if len(cache_values) > self.cache_size:
                json.dump(cache_values[-self.cache_size:], cache, default=GeoInfo.to_json, indent=2)
            else:
                json.dump(cache_values, cache, default=GeoInfo.to_json)

    def find_location_info(self):
        """
        Uses current list of IPs to find geo location info
        :return: list with geo location info
        """
        # Keep on making batch requests until list is over
        while self.ips_list:
            self.prepare_request_data()
            response = requests.post(self.url, json=self.request_data)
            data = list(response.json())

            # Fill GeoInfo data for every successful response
            for ip_info in data:
                for geo_info in self.geo_info_list[self.cur_geo_info_index:]:
                    if geo_info.ip == ip_info['query']:
                        if ip_info['status'] == 'success':
                            geo_info.fill_geo_info(ip_info['country'], ip_info['countryCode'], ip_info['region'],
                                                   ip_info['regionName'], ip_info['city'], ip_info['zip'],
                                                   ip_info['timezone'], ip_info['lat'], ip_info['lon'], ip_info['isp'],
                                                   ip_info['as'])
                        else:
                            geo_info.fill_error_message(ip_info['message'])
                        # Update cache
                        self.cache[geo_info.ip] = geo_info
                        break

            # Update geo info list index
            self.cur_geo_info_index += len(self.request_data)

        # Update cache file at the end
        self.update_cache()

        return self.geo_info_list
