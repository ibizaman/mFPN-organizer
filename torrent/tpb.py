from datetime import datetime
from datetime import timedelta

import requests
from bs4 import BeautifulSoup


def search(domain, what, category, sub_category=None, order=None):
    order = order or CONSTANTS['order']['seeders']['des']
    category = get_category(category, sub_category)

    page = 0
    while True:
        url = '{domain}/search/{what}/{page}/{order}/{category}/'.format(
            domain=domain,
            what=what,
            category=category,
            order=order,
            page=page,
        )
        for item in parse_table(url):
            if item is None:
                return
            yield item
        page += 1


def details(domain, torrent_link):
    response = requests.get(domain + torrent_link)
    if response.status_code != 200:
        raise RuntimeError(response)

    parsed = BeautifulSoup(response.text, 'html.parser')

    details = {}
    for dt in parsed.findAll('dt'):
        key = dt.text.strip(':').lower()
        value = dt.find_next_sibling('dd')
        if key == 'files':
            details['num_files'] = int(value.text)
        elif key == 'info':
            if value.text == 'IMDB':
                details['imdb_link'] = value.a['href']
            else:
                details['info'] = value.text

    return details


def top(domain, category, sub_category=None):
    category = get_category(category, sub_category)

    url = '{domain}/top/{category}/'.format(
        domain=domain,
        category=category,
    )
    print(url)
    for item in parse_table(url):
        yield item


def get_category(category, sub_category=None):
    sub_category = sub_category or 'all'
    return CONSTANTS['category'][category][sub_category]


def get_all_categories():
    for category in CONSTANTS['category']:
        for sub_category in CONSTANTS['category'][category]:
            if sub_category == 'all':
                yield (category, None)
            else:
                yield (category, sub_category)


def parse_table(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(response)

    parsed = BeautifulSoup(response.text, 'html.parser')
    if not parsed.table:
        return None

    for row in parsed.table.findAll('tr'):
        tds = row.findAll('td')
        if not tds:
            continue # skip header
        detLink = tds[1].find('a', 'detLink')
        detDesc = tds[1].find('font', 'detDesc')
        uploaded, size, _ = detDesc.text.replace('\xa0', ' ').split(', ', 2)
        yield {
            'link': detLink['href'],
            'title': detLink.text,
            'magnet': tds[1].find(title='Download this torrent using magnet')['href'],
            'uploaded': read_time(uploaded.split(' ', 1)[1]),
            'size': read_size(size.split(' ', 1)[1]),
            'user': detDesc.a.text if detDesc.a else 'anonymous',
            'user_link': detDesc.a['href'] if detDesc.a else None,
            'seeders': int(tds[2].text),
            'leechers': int(tds[3].text),
        }


def read_size(text):
    value, unit = text.split(' ')
    value = float(value)

    value = value * 1024
    if unit == 'KiB':
        return value

    value = value * 1024
    if unit == 'MiB':
        return value

    value = value * 1024
    if unit == 'GiB':
        return value


def read_time(string):
    try:
        return datetime.strptime(string, '%m-%d %Y')
    except KeyboardInterrupt:
        raise SystemExit('Keyboard interrupt')
    except:
        try:
            time = datetime.strptime(string, '%m-%d %H:%M')
            time = time.replace(year=datetime.now().year)
            return time
        except KeyboardInterrupt:
            raise SystemExit('Keyboard interrupt')
        except:
            time = datetime.strptime(string, 'Y-day %H:%M')
            time = time.replace(year=datetime.now().year, day=datetime.now().day)
            time = time - timedelta(1)
            return time


CONSTANTS = {
    'order': {
        'name': {
            'des': 1,
            'asc': 2,
        },
        'uploaded': {
            'des': 3,
            'asc': 4,
        },
        'size': {
            'des': 5,
            'asc': 6,
        },
        'seeders': {
            'des': 7,
            'asc': 8,
        },
        'leechers': {
            'des': 9,
            'asc': 10,
        },
        'uploader': {
            'des': 11,
            'asc': 12,
        },
        'type': {
            'des': 13,
            'asc': 14,
        },
    },
    'category': {
        'all': {
            'all': 0,
        },
        'audio': {
            'all': 100,
            'music': 101,
            'audio_books': 102,
            'sound_clips': 103,
            'flac': 104,
            'other': 199,
        },
        'video': {
            'all': 200,
            'movies': 201,
            'movies_dvdr': 202,
            'music_videos': 203,
            'movie_clips': 204,
            'tv_shows': 205,
            'handheld': 206,
            'hd_movies': 207,
            'hd_tv_shows': 208,
            'three_dimensions': 209,
            'other': 299,
        },
        'applications': {
            'all': 300,
            'windows': 301,
            'mac': 302,
            'unix': 303,
            'handheld': 304,
            'ios': 305,
            'android': 306,
            'other': 399,
        },
        'games': {
            'all': 400,
            'pc': 401,
            'mac': 402,
            'psx': 403,
            'xbox360': 404,
            'wii': 405,
            'handheld': 406,
            'ios': 407,
            'android': 408,
            'other': 499,
        },
        'porn': {
            'all': 500,
            'movies': 501,
            'movies_dvdr': 502,
            'pictures': 503,
            'games': 504,
            'hd_movies': 505,
            'movie_clips': 506,
            'other': 599,
        },
        'other': {
            'ebooks': 601,
            'comics': 602,
            'pictures': 603,
            'covers': 604,
            'physibles': 605,
            'other': 699,
        },
    }
}
