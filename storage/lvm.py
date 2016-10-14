#!/usr/bin/env python2

"""
Display lvm volumes.

Usage:
    lvm [-s]

Install:
    sudo pip2 install docopt lvm2py mdstat
"""

from docopt import docopt
from lvm2py import LVM
import mdstat


def main(argv=None):
    args = docopt(__doc__, argv=argv)
    lvm = LVM()

    if args['-s']:
        summary(lvm)


def summary(lvm):
    raids = get_raids()
    raids_str = []
    for raid_name, raid in raids.iteritems():
        raids_str.append([raid_name, '[' + raid['personality'] + ']', str(raid['status']['non_degraded_disks']) + '/' + str(raid['status']['raid_disks'])] + ['/dev/' + n for n in raid['disks']])

    print pad(raids_str)
    print

    for vg in sorted(lvm.vgscan(), key=lambda x: x.name):
        print vg.name, int(vg.size('GiB')), 'GiB', '(' + str(int((1 - vg.free_size() / vg.size()) * 100)) + '%)'

        print '  Physical Volumes:'
        pvs = []
        for pv in sorted(vg.pvscan(), key=lambda x: x.name):
            name = pv.name
            if pv.name in raids:
                name += '[R]'
            pvs.append(['   ', name, int(pv.size('GiB')), 'GiB', '(' + str(int((1 - pv.free() / pv.size()) * 100)) + '%)'])
        print pad(pvs)

        print '  Logical Volumes:'
        lvs = []
        for lv in sorted(vg.lvscan(), key=lambda x: x.name):
            lvs.append(['   ', lv.name, int(lv.size('GiB')), 'GiB'])
        print pad(lvs)

        print


def get_raids():
    return {'/dev/' + k: v for k, v in mdstat.parse()['devices'].iteritems()}


def pad(rows):
    max_column_size = [0 for _ in xrange(len(rows[0]))]
    for row in rows:
        for i, col in enumerate(row):
            max_column_size[i] = max(max_column_size[i], len(str(col)))

    for row in xrange(len(rows)):
        for col in xrange(len(rows[row])):
            rows[row][col] = str(rows[row][col])
            rows[row][col] += ' ' * (max_column_size[col] - len(rows[row][col]))

    return '\n'.join(' '.join(x for x in row) for row in rows)


if __name__ == '__main__':
    main()
