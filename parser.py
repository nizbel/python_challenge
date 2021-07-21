import re

from parser_utils import is_valid_ip


class IPParser:
    ipRegex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

    def __init__(self, path=''):
        self.path = path

    def read_file(self):
        if self.path:
            with open(self.path, 'r') as file:
                while True:
                    line = file.readline()
                    if not line:
                        break
                    ips_found = self.parse(line)
                    if ips_found:
                        print('Found ips ', [ip for ip in ips_found])
                        # break

    def parse(self, text):
        ips = re.findall(self.ipRegex, text)
        valid_ips = filter(lambda ip: is_valid_ip(ip), ips)
        return list(valid_ips)


reader = IPParser('list_of_ips.txt')
reader.read_file()
