from .file import files_in_directory, make_hardlink, difference_on_inode
from ..utils.userinput import input, year_type
from ..utils.utils import flatten_list
from . import transmission as torrentclient
import argparse
import sys


folders = {'movie':'/srv/movies', 'serie':'/srv/series', 'music':'/srv/music'}
categories = list(folders.keys())


def printout(string):
    sys.stdout.write(str(string)+"\n")


def connect_torrent_client(args):
    return torrentclient.connect(torrentclient.settings_from_args(args))


def to_be_sorted(args):
    finished_files = set()
    try:
        client = connect_torrent_client(args)
        finished_files = torrentclient.get_finished_files(client)
    except torrentclient.TransmissionError as e:
        print('Cannot connect to torrent server: ' + str(e.original))
        return
    downloaded_files = files_in_directory(args.download_dir) & finished_files
    sorted_files = set(flatten_list([files_in_directory(dir) for c,dir in folders.items()]))
    to_be_sorted = difference_on_inode(downloaded_files, sorted_files)
    if args.list:
        [printout(file) for file in to_be_sorted]
        return
    sort_files(to_be_sorted, args)
    printout('done, goodbye!')


def sort_files(files, args):
    printout(str(len(files)) + ' file(s) to sort:')
    for i, file in enumerate(files, 1):
        printout('file ' + str(i) + ': "' + file.name + '"')
        if not input('sort file?', convert_to = bool):
            continue

        category = ask_for_file_category()
        name = ask_for_file_name(category)
        finale_path = getattr(args, category+'_dir') + '/' + name + file.extension

        printout('new file name: '+finale_path)
        okay = input('is that okay?', convert_to = bool)

        if okay:
            make_hardlink(file.path, finale_path)
            printout('file sorted!')
        else:
            printout('skipping file...')


def select_files_to_download(args):
    try:
        client = connect_torrent_client(args)
        all_files = torrentclient.get_all_files(client)
    except torrentclient.TransmissionError as e:
        print('Cannot connect to torrent server: ' + str(e.original))
        return

    if args.onlyselected:
        files_to_process = [f for f in all_files if f.selected]
    else:
        files_to_process = all_files

    printout(str(len(files_to_process)) + ' files to process')
    for i, f in enumerate(files_to_process):
        printout('file ' + str(i) + ': "' + f.name + '"')
        action = ask_if_select_file(f.selected)
        if action == 'skip':
            printout('skipping file')
            continue
        else:
            select = action == 'yes'
            torrentclient.set_file_select_state(client, f, select)
            if select:
                printout('file selected for download')
            else:
                printout('removed file from downloading files')



def downloaded_files(args):
    try:
        client = torrentclient.connect(torrentclient.settings_from_args(args))
    except torrentclient.TransmissionError as e:
        printout(e.original)
        return None


def ask_for_file_category():
    return input('category', enum = categories)


def ask_for_file_name(category):
    if category == 'movie':
        name = input('name')
        year = input('year', convert_to = year_type)
        extra = input('extra (optional)')
        if extra != '':
            extra = ' ' + extra
        return name + ' ' + str(year) + extra
    elif category == 'serie':
        name = input('show name')
        season = input(u'season \u0023)', convert_to = int)
        season_0 = "%02d" % season
        episode_0 = "%02d" % input(u'episode n\u0023', convert_to = int)
        extra = input('extra (optional)')
        if extra != '':
            extra = ' ' + extra
        return name + '/Season ' + str(season) + '/' + name + ' S' + str(season_0) + 'E' + str(episode_0) + extra
    elif category == 'music':
        raise NotImplementedError()
        pass


def ask_if_select_file(currently_downloading):
    if currently_downloading:
        text = '(currently downloading)'
    else:
        text = '(currently not downloading)'
    return input('download file ' + text, enum = ['yes', 'no', 'skip'])


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_sort = subparsers.add_parser('sort')
    parser_sort.add_argument('--download_dir', default='/srv/downloads')
    for category, folder in folders.items():
        parser_sort.add_argument('--' + category + '_dir', default=folder)
    parser_sort.add_argument('--list', action='store_true')
    parser_sort.set_defaults(func=to_be_sorted)

    parser_select = subparsers.add_parser('select')
    parser_select.add_argument('--onlyselected', action='store_true')
    parser_select.set_defaults(func=select_files_to_download)

    torrentclient.decorate_args_parser(parser)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()

