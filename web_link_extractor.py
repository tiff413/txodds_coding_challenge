"""
A Simple Producer/Consumer Web Link Extractor

*  Reads input of text that contains URLs
*  Extracts URLs from text
*  Extracts and prints all hyperlinks from parsing each URL

*  Dictionary of results, results_dict, is produced
*  URL extracting and hyperlink extracting are done concurrently using threads

Assumptions
*  URLs have no commas
*  Hyperlinks are taken from href tags when href=True
*  Results for duplicate URLs will be replaced with most recent extracted
   hyperlinks
"""
#===============================================================================
# IMPORT MODULES

from pathlib import Path
from urlextract import URLExtract

from bs4 import BeautifulSoup
import requests
import re

from threading import Thread

#===============================================================================
# DEFINE FUNCTIONS
def ProducerLinkExtractor(text_str, url_queue=[]):
    """Reads and extracts URLs from txt file. Pushes extracted URLs onto queue.

    Parameters
    ----------
    text_str : str
        String containing URLs to extract
    url_queue : list
        Queue of URLs to be parsed by the consumer

    Returns
    -------
    list
        url_queue
    """

    max_queue_size = 50

    # Assume URLs have no commas
    text_str = text_str.replace(","," ")

    # Use URLExtract to extract URLs
    extractor = URLExtract()
    urls = extractor.find_urls(text_str)

    # Append new URLs to end of URL queue
    url_queue += urls
    # If queue larger than max_queue_size, remove oldest entries
    if len(url_queue)>max_queue_size:
        url_queue = url_queue[-max_queue_size:]

    return url_queue


def ConsumerHyperlinkExtractor(url_queue, results_dict={}):
    """Pops first element of url_queue. Executes HyperlinkExtractor to extract
    hyperlinks. Adds results to results_dict.

    Parameters
    ----------
    url_queue : list
    results_dict : dict
    """
    if len(url_queue) > 0:
        url = url_queue.pop(0)
        url, hyperlinks_list = HyperlinkExtractor(url)
        if url is not None:
            results_dict[url] = hyperlinks_list

        ### PRINT RESULTS
        print(url, hyperlinks_list)

    return results_dict


def HyperlinkExtractor(url):
    """Extracts all hyperlinks from a url.

    Parameters
    ----------
    url : str

    Returns
    -------
    list
        List of all hyperlinks in inputted url
    """

    # Parse HTML. If invalid URL, return None
    try:
        response = requests.get(url)
    # If no schema, add "https://" to URL
    except requests.exceptions.MissingSchema:
        try:
            url = "https://"+url
            response = requests.get(url)
        except:
            return None, None

    # If valid URL, get list of hyperlinks in URL
    if response is not None:
        html = response.content
        soup = BeautifulSoup(html, features="lxml")

        # Find all hrefs
        hyperlinks_list = soup.find_all(href=True)
        hyperlinks_list = [line['href'] for line in hyperlinks_list]

        return url, hyperlinks_list

    return None, None

#===============================================================================
# EXECUTE

# Initiate variables
url_queue = []
results_dict = {}

# Read input from file
txt_file = "url_file.txt"
with open(txt_file) as f:
    text_str = f.read()

# Start ProducerLinkExtractor on a thread (to run concurrently with other threads)
producer_thread = Thread(target=ProducerLinkExtractor, args=(text_str,url_queue,))
producer_thread.start()

# Start ConsumerHyperlinkExtractor while ProducerLinkExtractor is running or
# while there are URLs in the queue
while (producer_thread.is_alive()) or (len(url_queue)>0):
    consumer_thread = Thread(target=ConsumerHyperlinkExtractor, args=(url_queue,results_dict,))
    consumer_thread.start()
