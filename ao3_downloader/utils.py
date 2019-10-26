import requests
import re
import urllib.parse

from bs4 import BeautifulSoup

def is_valid_url(url):
    series_pattern = re.compile('^https?://(archiveofourown|ao3).org/series/\d+$')
    work_pattern = re.compile('^https?://(archiveofourown|ao3).org/works/\d+(/chapters/\d+)?$')
    return series_pattern.match(url) or work_pattern.match(url)

def get_html_parser(url):
    # validate url
    if not is_valid_url(url):
        print("Error: invalid URL!")
        raise ValueError('Invalid AO3 URL: {url}'.format(url=url))
    r = requests.get(url)
    return BeautifulSoup(r.content, 'html.parser')

def parse_series_title(parser):
    return parser.find('h2', class_='heading').text.strip()

def parse_series_authors(parser):
    authors = parser.find('dl', class_='series meta group').find_all('a', rel='author')
    return [author.text for author in authors]

def parse_series_work_urls(parser):
    work_links = parser.find_all(href=work_url_filter)
    work_urls = ['https://archiveofourown.org' + work.get('href') for work in work_links]
    return work_urls

def work_url_filter(href):
    return href and re.compile('/works/\d+$').search(href)

def parse_work_title(parser):
    return parser.find('h2', class_='title heading').text.strip()

def parse_work_authors(parser):
    authors = parser.find('h3', class_='byline').find_all('a', rel='author')
    return [author.text for author in authors]

def parse_work_part(parser):
    position = parser.find('span', class_='position')
    if position:
        pattern = re.compile('Part (\d+) of the')
        part = pattern.match(position.text).groups()[0]
        return int(part)
    return 1

def parse_work_download_url(parser, file_format):
    download_links = parser.find_all(href=download_url_filter)
    download_urls = ['https://archiveofourown.org' + link.get('href') for link in download_links]
    for url in download_urls:
        if file_format in url:
            return url

def download_url_filter(href):
    return href and re.compile('/downloads/\d+/.+').search(href)

def get_filename_from_url(url):
    # url format: https://ao3.org/downloads/12345678/work.epub?updated_at=123456789
    # get the rightmost part of url after last /, then remove everything after the ?
    encoded_filename = url.rsplit('/', 1)[1].split('?')[0]
    decoded_filename = urllib.parse.unquote(encoded_filename)
    return sanitize_filename(decoded_filename)

def sanitize_filename(filename):
    # source: https://stackoverflow.com/a/43553331
    allowed_chars = ['.', '-', '_']
    def safe_char(c):
        return c if c.isalnum() or c in allowed_chars else '_'
    return "".join(safe_char(c) for c in filename).rstrip('_')
