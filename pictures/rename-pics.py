#!/usr/bin/env python

# sudo apt-get install libexiv2-dev python-pyexiv2
# sudo pacman -S python2-pyexiv2

import argparse
import os
import re
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
import utils  #pylint: disable=import-error,wrong-import-position


def main():
    p = argparse.ArgumentParser()
    p.add_argument('files')
    p.add_argument('format')
    p.add_argument('--date-format')
    p.add_argument('--original-regex')
    p.add_argument('--lower-extension', action='store_true')
    p.add_argument('-n', '--dry_run', action='store_true')

    args = vars(p.parse_args())
    if args.get('original_regex'):
        args.update(parse_original_regex(args.pop('original_regex')))

    images = (utils.exif.get_metadata(f) for f in utils.get_all_files(args['files'].split(',')))

    renames = rename_images(images, args['format'], args)

    n_renames = 0
    for original_name, new_name in renames:
        i = 0
        while os.path.isfile(new_name + ('_' + str(i) if i else '')):
            i += 1
        new_name += '_' + str(i) if i else ''

        print format_rename(original_name, new_name)
        if not args['dry_run']:
            os.rename(original_name, new_name)
        n_renames += 1

    if n_renames == 0:
        print 'All files have already correct name'


def parse_original_regex(arg):
    first_char = arg[0]
    args = arg.split(first_char)
    return {'original_regex': args[1], 'original_replacement': args[2]}


def rename_images(images, name_format, args):
    for i in images:
        try:
            i.read()
        except Exception as e:
            print 'WARNING', e
            continue
        original_name = i.filename
        new_name = rename_image(i, name_format, args)
        if not new_name or original_name == new_name:
            continue
        yield (original_name, new_name)


def rename_image(image, filename_format, args):
    dirname, basename, extension = utils.get_path_info(image.filename)

    mapping = {}
    if '{date}' in filename_format:
        image.read() # here to only load file if needed
        mapping['date'] = get_date_mapping(args.get('date_format'), image)
    if '{original}' in filename_format:
        mapping['original'] = get_original_mapping(basename, args['original_regex'], args['original_replacement'])
    if args.get('lower_extension'):
        extension = extension.lower()

    if any(v is None for v in mapping.values()):
        return None

    new_basename = filename_format.format(**mapping)
    return utils.merge_path_info(dirname, new_basename, extension)


def get_date_mapping(date_format, image):
    if date_format is None:
        date_format = '%Y-%m-%d %H:%M:%S'
    try:
        date = image['Exif.Photo.DateTimeOriginal'].value
        return date.strftime(date_format)
    except KeyError:
        print 'ERROR: no Exif.Photo.DateTimeOriginal exif tag found in', image.filename
        return None


def get_original_mapping(original, regex, replacement):
    if regex is None:
        return original
    return re.sub(regex, replacement, original)


def format_rename(original_name, new_name):
    color_endc = '\033[0m'
    color_original = '\033[91m'
    color_new = '\033[94m'

    same_pos = 0
    while original_name[same_pos] == new_name[same_pos]:
        same_pos += 1

    return original_name[:same_pos] \
        + color_original \
        + original_name[same_pos:] \
        + color_endc \
        + ' -> ' \
        + new_name[:same_pos] \
        + color_new \
        + new_name[same_pos:] \
        + color_endc


if __name__ == '__main__':
    main()
