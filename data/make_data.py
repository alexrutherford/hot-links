import re
import sys
from types import NoneType
import dateutil
import requests
from bs4 import BeautifulSoup
import json
import logging
import pandas as pd
import dateutil
import time
import datetime

logging.basicConfig(filename='out.log', filemode='a', level=logging.DEBUG)

logger = logging.getLogger(__name__)

def get_date_from_url(url: str):
    '''Parses Guardian URLs to extract year, month and date'''
    pattern = re.compile(
    r"^https://www\.theguardian\.com/(?:[a-z-]+/)+"
    r"(20(0[0-9]|1[0-9]|2[0-4]))/"              # group 1 = full year 200 - 2024
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/"  # group 3 = month
    r"(0[1-9]|[12][0-9]|3[01])/"         # group 4 = day
    r"(?:[a-z0-9-]+)(?:/[a-z0-9-]+)*/?(?:[?#].*)?$")
    
    match = pattern.match(url.strip())
    
    
    if match:
        year = match.group(1)        # "2015"
        month = match.group(3)   # "oct"
        day = match.group(4)         # "21"
    
        # Parse with strptime
        dt = datetime.datetime.strptime(f"{match.group(1)} {match.group(3)} {match.group(4)}", "%Y %b %d")
        return dt
    else:
        return None

#####
def is_article(url: str) -> bool:
    """
    Checks if the given URL is an article from The Guardian and not the home page etc

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL starts with 'https://www.theguardian.com/', False otherwise.
    """
    
    pattern = re.compile(
    r"^https://www\.theguardian\.com/"
    r"(?:[a-z-]+/)+"                 # one or more section segments
    r"(20\d{2})/"                     # year, e.g. 2016
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/"  # month
    r"(0[1-9]|[12][0-9]|3[01])/"     # day
    r"[a-z0-9-]+(?:/[a-z0-9-]+)*/?$" # slug (one or more segments)
)

    # Got this with help from chatGPT
    if pattern.match(url):
        return True
    return False

#####
def save_links(blob : json) -> NoneType:
    """Saves JSON blob to file"""
    with open('../data/external/{:s}.json'.format(blob['id']), 'a') as f:
        json.dump(blob, f)

def extract_links_main(url: str, get_content = False) -> list:
    """Extracts links from the main content of the given URL and optionally also main body text"""
    time.sleep(0.5)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    links = []
    
    try:
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print('Failed',e)
        logger.warning('Failed {e}')
        logger.warning('URL: {url}')

    main = soup.find('div', id='maincontent')
    if main:
        soup = main
    else:
        if get_content:
            return [],''
        else:
            return []

    for a in soup.find_all('a', href=True):
        links.append({'href': a['href'], 'link': a.get_text(strip=True)})

    if get_content:
        return links,soup.text
    else:
        return links

#####
def extract_links(url: str) -> list:
    """
    Extracts links from the given URL.

    Args:
        url (str): The URL to extract links from.

    Returns:
        list: A list of dictionaries containing 'href' and 'link' for each extracted link.
    """
    # TODO fold this into get_links
    import time
    time.sleep(0.5)
    # In case we get 429s for too many requests
    
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    links = []
    
    try:
        content = soup.find('div', {'data-gu-name': "body"}).get_text(strip=True)
    except:
        logging.debug('No body content found')

    main = soup.find('main')
    if main:
        soup = main
    for a in soup.find_all('a', href=True):
        links.append({'href': a['href'], 'link': a.get_text(strip=True)})
    return links


#####
def get_links(blob: json,metadata: bool = False, v: bool = False) -> dict:
    """Extracts links from the given JSON blob."""
    url = blob['webUrl']
    id = str(blob['id'])

    logging.debug(url)

    logging.debug('URL: {:s}'.format(url))
    logging.debug('ID: {:s}'.format( id))

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    res = {}
    res['url'] = url
    res['id'] = id
    res['links'] = []
    
    try:
        res['bodyContent'] = soup.find('div', {'data-gu-name': "body"}).get_text(strip=True)
    except:
        res['bodyContent'] = ''
        logging.debug('No body content found')

    main = soup.find('main')
    if main:
        soup = main

    for a in soup.find_all('a', href=True):
        res['links'].append({'href': a['href'], 'link': a.get_text(strip=True)})

    logging.debug('Got links ({:d})'.format(len(res['links'])))

    if metadata:
       
        try:
            res['date'] = soup.find('span', class_=['dcr-u0h1qy','dcr-lp0nif']).get_text(strip=True)
            # If date is missing page is not a proper article
            # e.g. https://www.theguardian.com/football/boavista
            
            res['date'] = re.sub(r'\.',':',res['date'])
            res['date'] = dateutil.parser.parse(res['date'][0:-4], dayfirst = True)
        except Exception as e:
            logging.debug('Date error',e)
            
            
            try:
                res['date'] = soup.find('div', class_=['dcr-u0h1qy','dcr-lp0nif']).get_text(strip=True)
                logging.debug('div found')
            except:
                res['date'] = pd.NaT     
        
        logging.debug('Date done')

        
        try:
            res['title'] = soup.find('h1').get_text(strip=True) # , class_=['dcr-uc7bn6','dcr-wli6lg','dcr-1vit58r']
        except:
            logging.debug('No h1 found')
            
            try:
                res['title'] = soup.find('div', class_=['dcr-uc7bn6','dcr-wli6lg','dcr-1vit58r']).get_text(strip=True)
                logging.debug('Found div')
            except:
                logging.debug('No div found')
                res['title'] = ''

        
        # TODO Add section etc later
        
    if not metadata:
        return res
    else:
        return res