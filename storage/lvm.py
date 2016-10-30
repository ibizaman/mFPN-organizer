#!/usr/bin/env python2

"""
Display lvm volumes.

Usage:
    lvm [-s]

Install:
    sudo pip2 install docopt lvm2py mdstat
"""

import os
import sys

from docopt import docopt
from lvm2py import LVM
import mdstat
import parted

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import pad, columns, human_number  #pylint: disable=import-error,wrong-import-position


def main(argv=None):
    args = docopt(__doc__, argv=argv)

    if args['-s']:
        summary()
    else:
        summary()


def summary():
    used_devices = {}

    mounts = get_mounts(used_devices)

    output_raid = print_raid(used_devices)

    output_lvm = print_lvm(mounts, used_devices)

    output_mounts = print_mounts(mounts)

    output_devices = print_devices(used_devices)

    print '\n'.join(columns(output_raid, output_lvm, output_mounts, output_devices))


def print_raid(used_devices):
    output = [[' Raid '], []]
    raids = get_raids()
    for raid_name, raid in raids.iteritems():
        used_devices.update({'/dev/' + n: 'R' for n in raid['disks']})
        output.append([raid_name, '[' + raid['personality'] + ']', str(raid['status']['non_degraded_disks']) + '/' + str(raid['status']['raid_disks'])])
        for d in raid['disks']:
            output.append(['  ' + '/dev/' + d])

    return pad(output)


def print_lvm(mounts, used_devices):
    output = [' LVM ', '']
    lvm = LVM()
    for vg in sorted(lvm.vgscan(), key=lambda x: x.name):
        output.append(' '.join([vg.name, human_number(vg.size('KiB'), 'KiB'), '(' + str(int((1 - vg.free_size() / vg.size()) * 100)) + '%)']))

        vs = []
        for pv in sorted(vg.pvscan(), key=lambda x: x.name):
            name = pv.name
            used_devices[name] = 'L'
            vs.append([' P ', name, human_number(pv.size('KiB'), 'KiB'), '(' + str(int((1 - pv.free() / pv.size()) * 100)) + '%)'])

        for lv in sorted(vg.lvscan(), key=lambda x: x.name):
            used = mounts.get('/dev/mapper/' + vg.name + '-' + lv.name, {'used': ''})['used']
            vs.append([' L ', lv.name, human_number(lv.size('KiB'), 'KiB'), used])

        output += pad(vs)

    return output


def print_devices(used_devices):
    output = [' Devices ', '']
    for dev in sorted(parted.getAllDevices(), key=lambda x: x.path):
        output.append(dev.path + ' ' + dev.model + ' ' + human_number(dev.getSize(), 'MiB'))
        try:
            partitions = []
            disk = parted.Disk(dev)
            for partition in disk.partitions:
                used = ' ' + used_devices.get(partition.path, '') + ' '
                partitions.append([used, partition.path, human_number(partition.getLength() * partition.geometry.device.sectorSize)])
            if partitions:
                output += pad(partitions)
        except parted.DiskLabelException:
            pass

    return output


def get_raids():
    return {'/dev/' + k: v for k, v in mdstat.parse()['devices'].iteritems()}


def get_mounts(used_devices):
    mounts = {}
    with open('/proc/mounts') as f:
        for line in f.read().split('\n'):
            try:
                fs_name, mount_point, fs_type = line.split()[:3]
                used_devices[fs_name] = 'M'

                stat = os.statvfs(mount_point)
                total = stat.f_blocks * stat.f_frsize
                used = '(' + str(int((1 - float(stat.f_bfree) / stat.f_blocks) * 100)) + '%)'
                mounts[fs_name] = {'mount_point': mount_point, 'fs_type': fs_type, 'used': used, 'total': human_number(total)}
            except:
                pass

    return mounts


def print_mounts(mounts):
    output = [' Mounts ', '']

    mnts = []
    for fs_name, mount in sorted(mounts.iteritems(), key=lambda k: k[0]):
        mnts.append([fs_name, mount['fs_type'], mount['total'], mount['used']])
        mnts.append(['  ' + mount['mount_point']])

    output += pad(mnts)
    return output


if __name__ == '__main__':
    main()
