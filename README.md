Purpose
======
Python3 module used to rename and organize downloaded files.

Some hypothesis are done:
* You are using transmission-server to download files
* The files are all downloaded in the same folder


Connection
==========
Common to every command are the parameters to connect to transmission:
```
python3 organizer.py --transmission_host=localhost --transmission_port=9091 --transmission_auth='user:password'
```
Here, defaults are shown. You can thus omit the arguments whose default
value suits you.


Sort
====
The `sort` command is used to organize not yet organized files. It works
by asking you, for each file, first which category the file is and then
based on that:
* If it is a movie: the name, year and an optional extra text (used e.g.
  for CD indication)
* If it is a serie: TODO
* If it is a music: TODO

Default usage:
```
python3 organizer.py sort
```

Specify folders (here defaults are shown):
```
python3 organizer.py sort --download_dir='/srv/downloads' \
                          --movie_dir='/srv/movies' \
                          --music_dir='/srv/music' \
                          --serie_dir='/srv/series'
```

Only list files that are not sorted (i.e. make a dry-run):
```
python3 organizer.py sort --list
```

Of course, you can mix all those arguments together.


Select
======
The `select` command is used to choose which files you want to download.

Default usage:
```
python3 organizer.py sort
```

If you only want to process the files that are currently downloading and automatically skip the not downloading files:
```
python3 organizer.py sort --onlyselected
```
