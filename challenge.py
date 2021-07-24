#!/usr/bin/env python
import argparse
import json
import string
import random
from pathlib import Path

from geo_locator import GeoLocator, GeoInfo
from parser import IPParser
from rdap_manager import RDAPManager


def generate_random_string(size):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))

if __name__ == "__main__":
    files_read_folder = 'files_read'
    # Create read files folder if doesn't exist
    Path(files_read_folder).mkdir(exist_ok=True)

    # Parse file argument
    parser = argparse.ArgumentParser(description='Read file to search for IPs and realize Geo IP and RDAP lookups')
    parser.add_argument('--file', metavar='path', required=True,
                        help='the path to the file')
    args = parser.parse_args()

    file_path = args.file
    reader = IPParser(file_path)
    ips = reader.read_file()

    geo_locator = GeoLocator(verbose=True)
    rdap_manager = RDAPManager(verbose=True)

    # Prepare lists to gather info
    geo_info = []
    rdap_info = []

    # Prepare batch info
    ip_index = 0
    batch_size = 200
    ip_amount = min(batch_size, len(ips))

    # Process info in batches
    while ip_index < len(ips):
        geo_locator.set_ip_list(ips[ip_index: ip_index + ip_amount])
        geo_info.append(geo_locator.find_geo_location_info())

        rdap_manager.set_ip_list(ips[ip_index: ip_index + ip_amount])
        rdap_info.append(rdap_manager.find_rdap_info())

        ip_index += batch_size
        ip_amount = min(batch_size, len(ips) - ip_index)

    # Generate json files

    # Generate random files and map through files.json
    geo_info_file_path = f'{files_read_folder}/{generate_random_string(8)}.json'
    with open(geo_info_file_path, 'w') as new_geo_info_file:
        json.dump(geo_info, new_geo_info_file, default=GeoInfo.to_json)

    rdap_info_file_path = f'{files_read_folder}/{generate_random_string(8)}.json'
    with open(rdap_info_file_path, 'w') as new_rdap_info_file:
        json.dump(rdap_info, new_rdap_info_file)

    manager_file_path = 'files_read.json'
    files_read_list = []
    try:
        with open(manager_file_path, 'r') as manager_file:
            # Get current list of files read
            files_read_list = json.load(manager_file)
            if isinstance(files_read_list, dict):
                files_read_list = [files_read_list, ]

            file_read_info = {'file': file_path, 'geo_info': geo_info_file_path,
                              'rdap_info': rdap_info_file_path}

            files_read_list.append(file_read_info)

        with open(manager_file_path, 'w') as manager_file:
            json.dump(files_read_list, manager_file)
    except FileNotFoundError:
        # Initialize cache file
        with open(manager_file_path, 'w') as manager_file:
            file_read_info = {'file': file_path, 'geo_info': geo_info_file_path,
                              'rdap_info': rdap_info_file_path}

            files_read_list.append(file_read_info)
            json.dump(file_read_info, manager_file)


