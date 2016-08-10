#!/usr/bin/env python

import argparse
import os
import re
import traceback

def keep_by_order(match, files):
    s_files = sorted(files)
    for m in match:
        for f in s_files:
            if re.match(m, f):
                return f


def remove_files(files):
    for f in files:
        try:
            os.unlink(f.replace('\\', ''))
        except:
            traceback.print_exc()


def delete_first_files(keep, files):
    m = keep_by_order(keep, files)
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


def main():
    p = argparse.ArgumentParser()
    p.add_argument('fdupes_file')
    p.add_argument('keep')
    p.add_argument('--same_line', action='store_true')
    p.add_argument('--remove', action='store_true')

    args = p.parse_args()

    lines = open(args.fdupes_file).read().split('\n')
    dupes = split_lines(lines, same_line=args.same_line)
    keep_order = args.keep_order.split(',')
    for files in dupes:
        deleted = delete_first_files(keep, files)
        print(' '.join(format_file(f, f in deleted) for f in sorted(files, key=lambda k: (k in deleted, k))))
        if args.remove:
            remove_files(deleted)


if __name__ == '__main__':
    main()

