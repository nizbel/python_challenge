import re

from parser_utils import is_valid_ip


class IPParser:
    ipRegex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

    def __init__(self, path=''):
        self.path = path

    def read_file(self):
        if self.path:
            ips_found = []
            with open(self.path, 'r') as file:
                while True:
                    line = file.readline()
                    if not line:
                        break
                    line_ips = self.parse(line)
                    if line_ips:
                        ips_found.extend(line_ips)
            return ips_found

        raise ValueError('Path to text file is empty')

    def parse(self, text):
        """
        Parse IPs from a text string
        :param text: a string containing IPs
        :return: list of string IPs
        """
        ips = re.findall(self.ipRegex, text)
        valid_ips = filter(lambda ip: is_valid_ip(ip), ips)
        return list(valid_ips)


