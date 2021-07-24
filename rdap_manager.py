import json
import requests
import time

from threading import Thread


class RDAPLookupThread(Thread):
    def __init__(self, request_url, ip, manager):
        self.request_url = request_url
        self.ip = ip
        self.manager = manager
        super().__init__()

    def run(self):
        try:
            response = requests.get(self.request_url + self.ip)
            data = response.json()

            # Filter info we'll gather
            # if 'entities' in data and 'status' in data:
            rdap_info = {'entities': data['entities'], 'status': data['status'], 'ip': self.ip}
            # else:
            #     rdap_info = {'entities': [], 'status': '', 'ip': self.ip}

            # Update RDAP information list in manager
            self.manager.rdap_info_list.append(rdap_info)
            # Update cache
            self.manager.cache[self.ip] = data
        except Exception as e:
            # template = "An exception of type {0} occured. Arguments:\n{1!r}"
            # message = template.format(type(e).__name__, e.args)
            # print(message)
            print(f'Retrying {self.ip}')
            # Add url for retry
            self.manager.ips_list.append(self.ip)


class RDAPManager:
    # URLs retrieved from ipwhois docs
    urls = ['http://rdap.arin.net/registry/ip/',
            'http://rdap.db.ripe.net/ip/',
            'http://rdap.apnic.net/ip/',
            'http://rdap.lacnic.net/rdap/ip/',
            'http://rdap.afrinic.net/rdap/ip/'
            ]

    cache_size = 10000
    cache_file = 'cache/.rdapcache'

    def __init__(self, ips_list=[], threads_amount=4, verbose=False):
        self.ips_list = list(ips_list)
        self.rdap_info_list = []
        self.current_url_index = 0

        # Prepare cache
        self.cache = {}
        self.load_cache()

        # Prepare threads
        self.thread_amount = threads_amount
        self.threads = []

        self.verbose = verbose

    def load_cache(self):
        """
        Load cache from .cache file
        """
        try:
            with open(self.cache_file, 'r') as cache:
                rdap_info_list = json.load(cache)
                for rdap_info in rdap_info_list:
                    self.cache[rdap_info['ip']] = rdap_info

            print('RDAP cache size:', len(self.cache.keys()))
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

    def check_ip_in_cache(self, ip):
        """
        Checks if IP is already in cache
        :param ip: string containing IP
        :return: True if IP is in cache, False otherwise
        """
        # Check for cached ips
        if ip in self.cache:
            self.rdap_info_list.append(self.cache[ip])
            return True
        return False

    def update_cache(self):
        """
        Writes cache info to .cache file
        """
        with open(self.cache_file, 'w') as cache:
            cache_values = list(self.cache.values())
            if len(cache_values) > self.cache_size:
                json.dump(cache_values[-self.cache_size:], cache)
            else:
                json.dump(cache_values, cache)

    def get_current_url(self):
        """
        Returns the current used url and sets the index for the next one on the list
        :return: current url by the index value
        """
        current_url = self.urls[self.current_url_index]
        self.current_url_index += 1
        if self.current_url_index == len(self.urls):
            # Returns to first url
            self.current_url_index = 0
        return current_url

    def find_rdap_info(self):
        """
        Uses current list of IPs to find RDAP info
        :return: list with RDAP info
        """
        # Keep on making requests until list is over
        while self.ips_list:
            ip = self.ips_list.pop()
            if not self.check_ip_in_cache(ip):
                new_thread = RDAPLookupThread(self.get_current_url(), ip, self)
                new_thread.start()
                self.threads.append(new_thread)
                if self.verbose:
                    print(f'(RDAP) IPs remaining {len(self.ips_list)}')

                # Check if any thread ended
                while len(self.threads) == self.thread_amount and all([thread.is_alive() for thread in self.threads]):
                    time.sleep(2)

                # Remove empty threads
                self.threads[:] = [thread for thread in self.threads if thread.is_alive()]

        # Update cache file at the end
        self.update_cache()

        return self.rdap_info_list
