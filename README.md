Purpose
======
Python3 module used to rename and organize downloaded files.

Some hypothesis are done:
* You are using transmission-server to download files
* The files are all downloaded in the same folder

Usage
=====
Default usage:
```
python3 organizer.py sort
```

Specify transmission options (here defaults are shown):
```
python3 organizer.py --transmission_host=localhost --transmission_port=9091 --transmission_auth='user:password' sort
```

Specify folders (here defaults are shown):
```
python3 organizer.py sort --download_dir='/srv/downloads' --movie_dir='/srv/movies' --music_dir='/srv/music' --serie_dir='/srv/series'
```

Only list files that are not sorted:
```
python3 organizer.py sort --list
```

Of course, you can mix all those arguments together.
