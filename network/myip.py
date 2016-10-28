#!/usr/bin/env python3

"""
Query public ip and update remote location.

Usage:
    myip [-v] [-c <config>] [-t <temp>]
    myip setup

Options:
    -c <config>  Configuration path [default: /etc/mFPN-organizer/myip.conf]
    -t <temp>    Temporary directory [default: /tmp/mFPN-organizer/]
    -v           Verbose mode
"""

# TODO: store temporary ips in postgres
# TODO: store ips in remote postgres + godaddy and remove myip.sh

import os
import sys
from pprint import pprint

from docopt import docopt
import json
import yaml

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils


IPIFY_URL = "https://api.ipify.org?format=json"

GODADDY_URL = "https://api.godaddy.com/v1"
GODADDY_URL_DOMAIN = GODADDY_URL + "/domains/{domain}"
GODADDY_URL_A_RECORD = GODADDY_URL_DOMAIN + "/records/A/{name}"
GODADDY_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'sso-key {key}:{secret}'
}


def current_ip_ipify():
    r = requests.get(IPIFY_URL)
    r.raise_for_status()
    return r.json()['ip']


def previous_ip(temp_path):
    return next(utils.read_file_or_empty(os.path.join(temp_path, 'myip.prev_ip')))


def store_ip(temp_path, ip):
    utils.ensure_path_exists(temp_path)
    with open(os.path.join(temp_path, 'myip.prev_ip'), 'w') as f:
        f.write(ip)


def godaddy_set_ip(domain, name, key, secret, ip):
    url = GODADDY_URL_A_RECORD.format(domain=domain, name=name)

    headers = GODADDY_HEADERS
    headers['Authorization'] = headers['Authorization'].format(key=key, secret=secret)

    r = requests.put(url, headers=headers, data=json.dumps({'data': ip}))
    if r.status_code != 200:
        pprint(dict(r.headers))
        pprint(r.text)
        r.raise_for_status()


def main(argv=None):
    args = docopt(__doc__, argv=argv)
    config = yaml.safe_load(open(args['-c']).read())
    verbose = lambda *a: print(*a) if args['-v'] else None
    temp_path = args['-t']

    ip = current_ip_ipify()
    verbose('Current ip: "{}"'.format(ip))

    prev_ip = previous_ip(temp_path)
    verbose('Previous ip: "{}"'.format(prev_ip))

    if ip == prev_ip:
        verbose('Same current and previous ips, stopping here')
        return

    print('New ip: "{}"'.format(ip))

    store_ip(temp_path, ip)

    if 'godaddy' in config and config['godaddy'].get('enable'):
        g = config['godaddy']
        verbose('Updating godaddy domain "{domain}" A record "{record}"'.format(domain=g['domain'], record=g['name']))
        godaddy_set_ip(g['domain'], g['name'], g['key'], g['secret'], ip)


if __name__ == '__main__':
    main()

