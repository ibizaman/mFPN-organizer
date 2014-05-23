from transmissionrpc import Client, TransmissionError
from file import File
from utils import flatten_list


default_uri = "http://localhost:9091"


class FileState(File):
    def __init__(self, path, torrent, id, file):
        super().__init__(path, file['name'])
        self.id = id
        self.torrent = torrent
        self.selected = file['selected']
        self.completed = file['size'] == file['completed']


def decorate_args_parser(parser):
    parser.add_argument('--transmission_host', default='localhost')
    parser.add_argument('--transmission_port', default=9091)
    parser.add_argument('--transmission_auth', help='user:password')


def settings_from_args(args):
    return {
            'host': args.transmission_host,
            'port': args.transmission_port,
            'auth': auth_setting_from_args(args)
        }


def auth_setting_from_args(args):
    auth = getattr(args, 'transmission_auth', None)
    if not auth:
        return None
    auth = auth.split(':', 1)
    return {'user': auth[0], 'password': auth[1]}


def to_rpcclient_settings(settings):
    rpc = { 'address': settings['host'], 'port': settings['port'] }
    if settings['auth']:
        rpc.update({ 'user': settings['auth']['user'], 'password': settings['auth']['password'] })
    return rpc


def connect(settings):
    return Client(**to_rpcclient_settings(settings))


def get_finished_files(client):
    return set([f for f in get_all_files(client) if f.completed])


def get_all_files(client):
    return [FileState(t.downloadDir, t, f_id, f) for t in client.get_torrents() for f_id,f in t.files().items()]


def set_file_select_state(client, file, state):
    files = client.get_files()
    files[file.torrent.id][file.id]['selected'] = state
    client.set_files(files)


def selected_files(torrent):
    return [f for i,f in torrent.files().items() if f['selected']]

