from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mFPN-organizer',
    version='0.1',
    description='my Friend Private Network orgranizer',
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.5.3',
        'requests==2.13.0',
        'docopt==0.6.2',
    ],
    extras_require={
        'dev': [
            'coverage==4.3.4',
            'ipython==5.2.2',
        ],
        'test': [
            'pytest==3.0.6',
            'pytest-cov==2.4.0',
        ],
    },
)
