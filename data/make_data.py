import re
import sys
import requests
from bs4 import BeautifulSoup
import json
import logging

logging.basicConfig(filename='example.log', filemode='a', level=logging.DEBUG)

logger = logging.getLogger(__name__)

def is_article(url: str) -> bool:
    """
    Checks if the given URL is an article from The Guardian and not the home page etc

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL starts with 'https://www.theguardian.com/', False otherwise.
    """
    if re.match(r'https://www.theguardian.com/', url):
        return True
    return False

def save_links(blob):
    with open('../data/external/{:s}.json'.format(blob['id']), 'a') as f:
        json.dump(blob, f)


def get_links(blob):
    url = blob['webUrl']
    id = str(blob['id'])

    logging.debug('URL: {:s}'.format(url))
    logging.debug('ID: {:s}'.format( id))

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    res = {}
    res['url'] = url
    res['id'] = id
    res['links'] = []
    
    main = soup.find('main')
    if main:
        soup = main

    for a in soup.find_all('a', href=True):
        res['links'].append({'href': a['href'], 'link': a.get_text(strip=True)})

    return res