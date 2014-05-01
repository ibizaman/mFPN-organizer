from file import files_in_directory, make_hardlink
from userinput import input, year_type
from utils import flatten_list
import transmission as torrentclient
import argparse
import sys


folders = {'movie':'/srv/movies', 'serie':'/srv/series', 'music':'/srv/music'}
categories = list(folders.keys())


def printout(string):
    sys.stdout.write(str(string)+"\n")


def to_be_sorted(args):
    finished_files = set()
    try:
        client = torrentclient.connect(torrentclient.settings_from_args(args))
        finished_files = torrentclient.get_finished_files(client)
    except torrentclient.TransmissionError as e:
        print('Cannot connect to torrent server: ' + str(e.original))
        return
    downloaded_files = files_in_directory(args.download_dir) & finished_files
    sorted_files = set(flatten_list([files_in_directory(dir) for c,dir in folders.items()]))
    to_be_sorted = downloaded_files - sorted_files
    if args.list:
        [printout(file) for file in to_be_sorted]
        return
    sort_files(to_be_sorted, args)
    printout('done, goodbye!')


def downloaded_files(args):
    try:
        client = torrentclient.connect(torrentclient.settings_from_args(args))
    except torrentclient.TransmissionError as e:
        printout(e.original)
        return None


def sort_files(files, args):
    printout(str(len(files)) + ' file(s) to sort:')
    for i, file in enumerate(files, 1):
        printout('file ' + str(i) + ': "' + file.name + '"')
        if input('skip file?', convert_to = bool):
            continue

        category = ask_for_file_category()
        name = ask_for_file_name()
        finale_path = getattr(args, category+'_dir') + '/' + name + file.extension

        printout('new file name: '+finale_path)
        okay = input('is that okay?', convert_to = bool)

        if okay:
            make_hardlink(file.path, finale_path)
            printout('file sorted!')
        else:
            printout('skipping file...')


def ask_for_file_category():
    return input('category', enum = categories)


def ask_for_file_name():
    name = input('name')
    year = input('year', convert_to = year_type)
    extra = input('extra (optional)')
    if extra != '':
        extra = ' ' + extra
    return name + ' ' + str(year) + extra


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_sort = subparsers.add_parser('sort')
    parser_sort.add_argument('--download_dir', default='/srv/downloads')
    for category, folder in folders.items():
        parser_sort.add_argument('--' + category + '_dir', default=folder)
    parser_sort.add_argument('--list', action='store_true')
    parser_sort.set_defaults(func=to_be_sorted)

    torrentclient.decorate_args_parser(parser)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

