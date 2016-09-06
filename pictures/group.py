#!/usr/bin/env python

"""
Group files by date.

Usage:
  group [-n] [-m] [-v] <destination> <input>...

<destination>  directory in which files are copied or moved
<input>        either a file, a folder or a glob pattern.
Examples:
  path/to/file.jpg
  path/to/folder
  /path/to/files*
  /path/**/files*


Options:
  -n --dry-run  only show what would be done, do not actually copy
                or move
  -m --move     move files instead of copying them
  -v --verbose  show exactly from which pictures groups are made from
"""

import os
import sys
from datetime import timedelta
from collections import defaultdict

from docopt import docopt

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import utils  #pylint: disable=import-error,wrong-import-position
print dir(utils)


def main(argv=None):
    args = docopt(__doc__, argv=argv)

    pictures = utils.get_all_files(args['<input>'])
    destination = args['<destination>']
    dry_run = args['--dry-run']
    move = args['--move']
    verbose = args['--verbose']

    groups = group_pictures(pictures)
    groups = group_consecutive_days(groups)

    for group, pics in groups.iteritems():
        print group, len(pics)

    send_to_destination(destination, groups, move=move, dry_run=dry_run, verbose=verbose)


def group_pictures(pictures):
    groups = defaultdict(list)
    for pic in pictures:
        try:
            exif = utils.exif.get_metadata(pic)
            exif.read()
        except Exception as e:
            print 'WARNING', e
        else:
            day = exif['Exif.Photo.DateTimeOriginal'].value.date()
            groups[day].append(pic)
    return dict(groups)


def group_consecutive_days(groups):
    prev_day = None
    consecutive_days = []
    for day in sorted(groups):
        if prev_day is None or (day - prev_day != timedelta(1)) or (day.month() != prev_day.month()):
            consecutive_days.append([day])
        else:
            consecutive_days[-1].append(day)
        prev_day = day

    consecutive_groups = {}
    day_format = '%Y-%m-%d'
    for days in consecutive_days:
        if len(days) == 1:
            name = days[0].strftime(day_format)
        else:
            name = days[0].strftime(day_format) + '_' + days[-1].strftime('%d')
        consecutive_groups[name] = [pic for day in days for pic in groups[day]]
    return consecutive_groups


def send_to_destination(destination, groups, move=False, dry_run=False, verbose=False):
    if not dry_run:
        utils.mkdir_p(destination)
    for day, pics in groups.iteritems():
        day_dir = os.path.join(destination, day)
        if not dry_run:
            utils.mkdir_p(day_dir)
        for pic in pics:
            dst_file = os.path.join(day_dir, os.path.basename(pic))
            if move:
                if verbose or dry_run:
                    print 'Moving {} to {}'.format(pic, dst_file)
                if not dry_run:
                    utils.move(pic, dst_file)
            else:
                if verbose or dry_run:
                    print 'Copying {} to {}'.format(pic, dst_file)
                if not dry_run:
                    utils.copy(pic, dst_file)


if __name__ == '__main__':
    main()
