#!/usr/bin/env python

"""
Enhanced management of fdupes output.

Usage:
  fdupes-dedupe [-1] [-f] [-v] <file> (<keep> | --not=<discard>)...

<file>     file output of fdupes
<keep>     regex of files you want to keep
<discard>  regex of files you don't want to keep

Example <keep> or <discard>:
  .*backup.*      keep all files with backup somewhere in the path

Options:
  -1 --same-line  set if fdupes was run with -1 argument too
  -f --remove     actually remove the files in red
"""

import os
import re
import traceback

from docopt import docopt


def main(argv=None):
    args = docopt(__doc__, argv=argv)

    fdupes_file = args['<file>']
    keep = args['<keep>']
    discard = args['--not']
    same_line = args['--same-line']
    remove = args['--remove']

    lines = open(fdupes_file).read().split('\n')
    dupes = split_lines(lines, same_line=same_line)
    for files in dupes:
        deleted = delete_first_files(keep, discard, files)
        print(' '.join(format_file(f, f in deleted) for f in sorted(files, key=lambda k: (k in deleted, k))))
        if remove:
            remove_files(deleted)


def keep_by_order(keep, discard, files):
    s_files = sorted(files)

    max_f = None
    max_sum = 0
    for f in s_files:
        sum_f = sum(bool(re.match(k, f)) for k in keep)
        if sum_f > max_sum:
            max_sum = sum_f
            max_f = f
    if max_sum > 0:
        return max_f

    max_f = None
    max_sum = 0
    for f in s_files:
        sum_f = sum(not re.match(d, f) for d in discard)
        if sum_f > max_sum:
            max_sum = sum_f
            max_f = f
    if max_sum > 0:
        return max_f


def remove_files(files):
    for f in files:
        try:
            os.unlink(f.replace('\\', ''))
        except:
            traceback.print_exc()


def delete_first_files(keep, discard, files):
    m = keep_by_order(keep, discard, files)
    f = set(files)
    if m:
        f.remove(m)
    elif f:
        f.remove(sorted(files)[0])
    return f


def split_lines(lines, same_line):
    if same_line:
        x = [set(i for i in re.split(r'(?<=[^\\]) ', x) if i != '') for x in lines]
    else:
        x = [set()]
        for i in lines:
            if i == '':
                x.append(set())
            else:
                x[-1].add(i)

    if x[-1] == set():
        del x[-1]
    return x


def format_file(file, is_deleted):
    ENDC = '\033[0m'
    FAIL = '\033[91m'

    if is_deleted:
        return FAIL + file + ENDC
    else:
        return file


if __name__ == '__main__':
    main()

