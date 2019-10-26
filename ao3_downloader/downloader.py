#!/usr/bin/python3.7
import pathlib
import requests

import re
import sys
import argparse
from time import sleep
from typing import NamedTuple

import utils

FORMATS = ['azw3', 'mobi', 'epub', 'pdf', 'html']

class Series(NamedTuple):
    title: str
    authors: list
    work_urls: list

class Work(NamedTuple):
    title: str
    authors: list
    part: int
    download_url: str
    filename: str
    # TODO: having multiple download options available

def parse_cli(argv):
    parser = argparse.ArgumentParser(description="AO3 Downloader")
    parser.add_argument('series', help='series URL')
    parser.add_argument('output', help='download destination folder')
    parser.add_argument('-f', '--fileformat', help='download file format -- {}'.format(FORMATS),
                        nargs='?', default='epub')
    args = parser.parse_args()

    series_url = args.series
    download_path = pathlib.Path(args.output)
    file_format = args.fileformat

    print("Series URL: {}".format(series_url))
    print("Download destination: {}".format(download_path))
    print("File format: {}".format(file_format))

    if series_url and download_path:
        try:
            download_series(series_url, download_path, file_format)
        except ValueError as e:
            print(e)
            sys.exit(1)

def download_series(series_url, download_path, file_format):
    '''
    given a series url, write all works in a series to files
    '''
    print("Downloading series...")
    series_metadata = get_series_metadata(series_url)
    print("Downloaded series metadata.\nSeries: {title}\nAuthors: {authors}\nWorks: {numworks}".format(
        title=series_metadata.title, authors=series_metadata.authors, numworks=len(series_metadata.work_urls)))

    # create series subfolder from series name and use as download path
    sanitized_series = utils.sanitize_filename(series_metadata.title)
    sanitized_authors = "_".join([utils.sanitize_filename(author) for author in series_metadata.authors])
    series_subfolder_path = download_path / "{}_by_{}".format(sanitized_series, sanitized_authors)

    if not series_subfolder_path.exists(): 
        try:
            series_subfolder_path.mkdir()
        except IOError as e:
            print(e)
            sys.exit(1)

    for work_url in series_metadata.work_urls:
        # TODO: break into metadata and download?
        download_work(work_url, series_subfolder_path, file_format, True)
        sleep(1)

def get_series_metadata(series_url):
    '''
    given series url, return Series object
    '''
    parser = utils.get_html_parser(series_url)
    title = utils.parse_series_title(parser)
    authors = utils.parse_series_authors(parser)
    work_urls = utils.parse_series_work_urls(parser)
    return Series(title, authors, work_urls)

def download_work(work_url, download_path, file_format, in_series=False):
    '''
    given work url, download work
    '''
    print("Downloading work metadata...")
    work_metadata = get_work_metadata(work_url, file_format)
    print("Downloaded metadata.\nWork: {title}\nAuthors: {authors}\nPart: {part}".format(title=work_metadata.title, authors=work_metadata.authors, part=work_metadata.part))
    try:
        prefix = "{:02d}-".format(work_metadata.part) if in_series else ""
        filename = "{}{}".format(prefix, work_metadata.filename)
        filepath = download_path / filename

        print("Downloading work at {}".format(filepath))
        work = requests.get(work_metadata.download_url).content
        with filepath.open(mode='wb') as fid:
            fid.write(work)
    except IOError as e:
        print(e)
        sys.exit(1)
    print("Downloaded {} by {}.".format(work_metadata.title, work_metadata.authors))

def get_work_metadata(work_url, file_format):
    parser = utils.get_html_parser(work_url)
    title = utils.parse_work_title(parser)
    authors = utils.parse_work_authors(parser)
    part = utils.parse_work_part(parser)
    download_url = utils.parse_work_download_url(parser, file_format)
    filename = utils.get_filename_from_url(download_url)
    return Work(title, authors, part, download_url, filename)

if __name__ == '__main__':
    parse_cli(sys.argv[1:])
