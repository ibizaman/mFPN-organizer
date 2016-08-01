Purpose
======
Python module used to rename and organize downloaded files.

Works with python 2 and 3.

Some hypothesis are done:
* You are using transmission-server to download files
* The files are all downloaded in the same folder


Install
=======
```
git clone https://github.com/ibizaman/mFPN-organizer
```


Connection
==========
Common to every command are the parameters to connect to transmission:
```
python3 -m mFPN-organizer --transmission_host=localhost --transmission_port=9091 --transmission_auth='user:password'
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
* If it is a serie: the name of the shown, the season number, the
  episode number and an optional extra text
* If it is a music: TODO

Default usage:
```
python3 -m mFPN-organizer sort
```

Specify folders (here defaults are shown):
```
python3 -m mFPN-organizer sort --download_dir='/srv/downloads' \
                               --movie_dir='/srv/movies' \
                               --music_dir='/srv/music' \
                               --serie_dir='/srv/series'
```

Only list files that are not sorted (i.e. make a dry-run):
```
python3 -m mFPN-organizer sort --list
```

Of course, you can mix all those arguments together.


Select
======
The `select` command is used to choose which files you want to download.

Default usage:
```
python3 -m mFPN-organizer select
```

If you only want to process the files that are currently downloading and automatically skip the not downloading files:
```
python3 -m mFPN-organizer select --onlyselected
```
