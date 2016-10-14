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

