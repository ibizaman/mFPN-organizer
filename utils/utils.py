import itertools
import re
import subprocess


def flatten_list(l):
    return [item for sublist in l for item in sublist]


def call(*args):
    return subprocess.Popen(args, stdout=subprocess.PIPE).stdout.read()


def keep_lines(lines, regex):
    for line in lines:
        if re.match(regex, line):
            yield line


def pad(rows, between=' '):
    max_column_size = [0 for _ in xrange(max(len(r) for r in rows))]
    for row in rows:
        for i, col in enumerate(row):
            max_column_size[i] = max(max_column_size[i], len(str(col)))

    for row in xrange(len(rows)):
        for col in xrange(len(rows[row])):
            rows[row][col] = str(rows[row][col])
            rows[row][col] += ' ' * (max_column_size[col] - len(rows[row][col]))

    return [between.join(x for x in row) for row in rows]


def columns(*lines):
    return pad([list(row) for row in itertools.izip_longest(*lines, fillvalue='')], between='  |  ')


def human_number(number, start_scale='B', round_digits=2):
    number = float(number)
    scale = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    current_scale = scale.index(start_scale)
    while int(number / 1024) > 0 and current_scale < len(scale) - 1:
        number = number / 1024
        current_scale += 1
    return str(round(number * 10**round_digits) / 10**round_digits) + ' ' + scale[current_scale]

