from transmissionrpc import Client, TransmissionError
from file import File
from utils import flatten_list


default_uri = "http://localhost:9091"


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
    all_torrents = client.get_torrents()
    files = []
    for t in only_downloaded(all_torrents):
        path = t.downloadDir
        for f in selected_files(t):
            files.append(File(path, f['name']))
    return set(files)


def only_downloaded(torrents):
    return [t for t in torrents if t.percentDone == 1.0]


def selected_files(torrent):
    return [f for i,f in torrent.files().items() if f['selected']]

