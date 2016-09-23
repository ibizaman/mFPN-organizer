#!/usr/bin/env python

"""
Copy directory structure

Usage:
  copy-structure <left> <right>

<left> <right>  result of `find $FOLDER -exec md5sum '{}' ';' | tee $FILE`
                on $FOLDER the folder where
"""

import os
import re
#import sys

from __builtin__ import open  # pylint: disable=redefined-builtin
from collections import defaultdict

from docopt import docopt

#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
#import utils  #pylint: disable=import-error,wrong-import-position
SPACES_REGEX = re.compile(r' +')


def main(argv=None):
    args = docopt(__doc__, argv=argv)

    left_file = args['<left>']
    right_file = args['<right>']

    left = make_directory_tree(parse_md5_file(left_file))
    right = make_directory_tree(parse_md5_file(right_file))

    remove_identical_subtrees(left, right)

    if not left and not right:
        print '# Nothing to do, left and right are identical'
        return True
    elif not right:
        print '# Nothing to do, right is a subset of left'
        return True

    moves = compute_moves(left, right)

    print format_moves(right, moves)


def parse_md5_file(filename):
    md5s = []
    with open(filename, 'r') as f:
        for line in f:
            md5, path = SPACES_REGEX.split(line.rstrip('\n'), 1)
            md5s.append((md5, path))
    return sorted(md5s, key=lambda v: v[1])


def make_directory_tree(md5s):
    paths = defaultdict(lambda: {'content': {}, 'children': {}})
    for md5, path in md5s:
        paths[os.path.dirname(path)]['content'][md5] = os.path.basename(path)
    for dirname in paths.iterkeys():
        if dirname != '':
            paths[dirname]['children'] = {d: v for d, v in paths.iteritems() if os.path.dirname(d) == dirname}
    return dict(paths)


def remove_identical_subtrees(left, right):
    for path in left.keys():
        if left[path] == right.get(path):
            del right[path]
            del left[path]


def compute_moves(left, right):
    moves = {'dirs': {}, 'files': {}}
    for rpath in right.keys():
        for lpath in left.keys():
            # Move the whole dir if content is equal
            if left[lpath] == right[rpath]:
                #if 'Day 7' in lpath and '11_12' in rpath:
                #    print left[lpath]
                #    print right[rpath]
                #    exit()
                #    print '!'
                del right[rpath]
                del left[lpath]
                moves['dirs'][rpath] = lpath
                break
            # Else, move file by file if they are equal
            else:
                for left_md5, left_f in left[lpath]['content'].items():
                    for right_md5, right_f in right[rpath]['content'].items():
                        if left_md5 != right_md5:
                            continue
                        rdir = rpath + '/' if rpath else ''
                        ldir = lpath + '/' if lpath else ''
                        del left[lpath]['content'][left_md5]
                        del right[rpath]['content'][right_md5]
                        moves['files'][rdir + right_f] = ldir + left_f
                        break

    graph_from = defaultdict(set)
    graph_to = defaultdict(set)
    print moves
    for from_path, to_path in moves['dirs'].iteritems():
        graph_from[from_path].add(to_path)
        graph_to[to_path].add(from_path)
    for from_path, to_path in moves['files'].iteritems():
        #if right.get(os.path.dirname(from_path)):
        #    continue
        graph_from[os.path.dirname(from_path)].add(os.path.dirname(to_path))
        graph_to[os.path.dirname(to_path)].add(os.path.dirname(from_path))

    print graph_from
    print graph_to

    for from_path, to_paths in graph_from.iteritems():
        if len(to_paths) != 1:
            continue
        to_path = to_paths.pop()
        if len(graph_to[to_path]) > 1:
            moves['dirs'][os.path.join(from_path, '*')] = to_path
        else:
            moves['dirs'][from_path] = to_path
        for from_move in moves['files'].keys():
            if os.path.dirname(from_move) != from_path:
                continue
            del moves['files'][from_move]
            if from_path in right:
                del right[from_path]

    for path, value in right.items():
        if value == {'content': {}, 'children': {}}:
            del right[path]
    return moves


def format_moves(right, moves):
    script = '#!/bin/sh\nset -e\n'

    # If things are remaining in right, then they were not moved.
    not_moved = set()
    if right:
        for path, value in right.iteritems():
            if path not in moves['dirs']:
                for f in value['content'].itervalues():
                    if os.path.join(path, f) not in moves['files']:
                        if path:
                            not_moved.add(os.path.join(path, f))
                        else:
                            not_moved.add(f)
    if not_moved:
        script += '# Did not move:\n'
        script += ''.join('# ' + f + '\n' for f in sorted(not_moved))

    mkdirs = set()
    mvs = set()
    # Moving directories
    #all_move_to_dirs = moves['dirs'].values()
    for move_from, move_to in moves['dirs'].iteritems():
        if move_from == move_to:
            continue
        #if all_move_to_dirs.count(move_to) > 1:
        #    star = '/*'
        #else:
        #    star = ''
        move_from = format_path(move_from)
        move_to = format_path(move_to)
        mkdirs.add('mkdir -p {to}'.format(to=move_to))
        mvs.add('mv {from} {to}'.format(**{'from': move_from, 'to': move_to}))

    # Moving files
    for move_from, move_to in moves['files'].iteritems():
        if move_from == move_to:
            continue
        to_dir = os.path.dirname(move_to)
        move_from = format_path(move_from)
        move_to = format_path(move_to)
        to_dir = format_path(to_dir)
        if to_dir != '':
            mkdirs.add('mkdir -p {to_dir}'.format(to_dir=to_dir))
        mvs.add('mv {from} {to}'.format(**{'from': move_from, 'to': move_to}))

    if mkdirs:
        script += '\n'.join(sorted(mkdirs)) + '\n'
    if mvs:
        script += '\n'.join(sorted(mvs)) + '\n'
    return script


def format_path(path):
    if ' ' in path:
        return '"{}"'.format(path)
    else:
        return path



if __name__ == '__main__':
    main()
