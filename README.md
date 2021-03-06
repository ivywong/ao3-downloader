# AO3 Downloader

Program to download AO3 series via command line (and eventually GUI).

Requires Python 3.6+, `bs4`, `requests`,`pysimplegui`.

Usage:
```
./downloader.py <series_url> <download_destination> -f <file_format>
```
OR
```
python3 gui.py
```

Example:
```
./downloader.py https://archiveofourown.org/series/1372270 /home/ivy/fics/ -f pdf
```

Series URL is the link to the series on AO3, e.g. `https://archiveofourown.org/series/1372270`.

Download destination is the folder where you want to store the downloaded series. Note that the script will create a subfolder for the series, so there's no need to do that manually.

File format is optional; valid file formats are `azw3`, `epub`, `mobi`, `pdf`, and `html`.

---

Screenshot:

![img](https://i.imgur.com/obTnAkk.jpg)
