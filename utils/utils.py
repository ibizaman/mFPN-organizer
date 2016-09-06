import errno
import hashlib
import os
import shutil
from glob import glob


def flatten_list(l):
    return [item for sublist in l for item in sublist]


def get_all_files(lst):
    if not isinstance(lst, list):
        lst = [lst]

    lst = (x for l in lst for x in glob(l))
    for l in lst:
        if os.path.isdir(l):
            for f in get_recursive_files_from_dir(l):
                yield f
        else:
            yield l


def get_recursive_files_from_dir(dir):
    all_files = []
    for dirpath, _, files in os.walk(dir):
        all_files += [os.path.join(dirpath, basename) for basename in files]
    return all_files


def get_path_info(path):
    dirname, _, basename = path.filename.rpartition(os.path.sep)
    basename, _, extension = basename.rpartition('.')
    return dirname, basename, extension


def merge_path_info(dirname, basename, extension):
    return os.path.join(dirname, basename) + '.' + extension


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def md5(path):
    return hashlib.md5(path).hexdigest()


def md5_file(path):
    return hashlib.md5(open(path).read()).hexdigest()


def copy(src, dst):
    shutil.copy2(src, dst)


def move(src, dst):
    shutil.move(src, dst)
