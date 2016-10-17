#!/usr/bin/env python3

"""
Maintains port forwardings on router.

Usage:
    ports [-c <config>]

Options:
    -c --config <config>  Config path to read from [default: /etc/mFPN-organizer/ports.conf]

"""

import os
import re
import sys

from docopt import docopt
import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils


def main(argv=None):
    args = docopt(__doc__, argv=argv)
    rules = yaml.load(open(args['--config']).read())

    existing_rules = get_existing_rules()

    for rule in rules:
        if rule in existing_rules:
            print('skipping rule', format(rule))
            continue

        print('enforcing rule', format(rule))
        command = ['upnpc', '-r', str(rule['port'])]
        if 'external_port' in rule:
            command += [str(rule['external_port'])]
        command += [rule['protocol']]
        utils.call(*command)


def get_existing_rules():
    command = ['upnpc', '-l']
    output = utils.call(*command).decode('utf-8').split('\n')
    rules_str = utils.keep_lines(output, r'.*\d->')
    rules = []
    for rule_str in rules_str:
        rule_str_split = re.split(r'\s+|->|:', rule_str)
        rule = {'port': int(rule_str_split[5]), 'protocol': rule_str_split[2].lower()}
        if int(rule_str_split[3]) != rule['port']:
            rule['external_port'] = int(rule_str_split[3])
        rules.append(rule)
    return rules


def format(rule):
    return str(rule['port']) + '->' \
        + str(rule.get('external_port', rule['port'])) \
        + ' ' + rule['protocol']


if __name__ == '__main__':
    main()
