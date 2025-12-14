"""
Module to scrape google scholar information. Inspired by dfm/cv/update-astro-pubs

author: @arjunsavel
"""
import inspect
import json
import os
import pdb
import random
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

# import cv
#
# cv_root = inspect.getfile(cv).split("cv")[0]
# data_path = os.path.join(cv_root, "data")


def clean_citation(citation):
    """
    cast the citation to an int.
    """
    if citation != "":
        citation = eval(citation)
    else:
        citation = 0
    return citation


def clean_authors(authors):
    """
    Reorders them like ADS.
    """
    # turn into a list
    authors = authors.split(", ")

    # flip them
    for i, author in enumerate(authors):
        # split into initials and last name
        if author in ["...", " "]:
            break
        split_author_name = author.split()
        author = split_author_name[-1] + ", " + split_author_name[0]
        authors[i] = author

    return authors


def clean_journal_info(journal_info):
    """
    Separates the string containing journal info into a dictionary containing the parameters as ADS does.

    Inputs
    ------
        :journal_info: (str) information about the journal, e.g. its name and the page

    Outputs
    -------
        :journal_info_split_cleaned:  (list of strs) all the info from the journal but split up.
    """
    journal_info_split_cleaned = {}
    if "arxiv" in journal_info:
        journal_info_split_cleaned["arxiv"] = journal_info.split(":")[-1]
        journal_info_split_cleaned["journal"] = "arxiv"
        return

    journal_info_split = journal_info.split(", ")
    # pdb.set_trace()
    print(journal_info_split)
    year = eval(journal_info_split[-1])  # the year is always the last

    journal_info_split_cleaned["page"] = None
    journal_info_split_cleaned["volume"] = None
    journal_info_split_cleaned["arxiv"] = None
    journal_info_split_cleaned["journal"] = journal_info_split[0]

    if len(journal_info_split) == 3:  # just journal and year
        journal_info_split_cleaned["page"] = journal_info_split[1]

    journal_info_split_cleaned["year"] = year

    return journal_info_split_cleaned


def get_scrape_google_scholar(author_id, api_key):
    """
    Does the main google scholar scraping for all pubs for an author.

    Inputs
    -------
        :author: (str) name of author. lastname, firstname midddlename.

    Outputs
    -------
        :cleaned_articles: list of dict of publications.
    """
    # author = reverse_name(author)


    # Your SerpAPI key (get it from https://serpapi.com/)
    API_KEY = api_key

    # The URL
    url = 'https://serpapi.com/search.json?author_id=e6T8gFsAAAAJ&engine=google_scholar_author&hl=en'

    # Query parameters
    params = {
        "engine": "google_scholar_author",
        "author_id": "e6T8gFsAAAAJ",
        "hl": "en",
        "api_key": API_KEY
    }

    # Make the GET request
    response = requests.get(url, params=params)

    # Parse JSON
    data = response.json()

    h_index = data['cited_by']['table'][1]['h_index']['all']
    paper_dict = data['articles']
    n_citations = data['cited_by']['table'][0]['citations']['all']
    # now just need first author citations
    citations = []
    for article in data['articles']:
        authors = article['authors'].split(',')
        if 'mcdanal' in authors[0].lower():
            citation = article['cited_by']['value']
            if citation is not None:
                citations += [citation]
    citations = np.array(citations)
    n_first_author_citations = np.sum(citations)
    first_author_h_index = calc_h_index(citations)
    return paper_dict, n_citations, h_index, n_first_author_citations, first_author_h_index


def reverse_name(author):
    """
    goes from lastname, firstname middlename to firstname, lastname.
    todo: multiple middle names?
    """

    author_names = author.replace(",", "").split(" ")

    if len(author_names) == 3:
        return " ".join([author_names[1], author_names[2], author_names[0]])
    else:
        return " ".join([author_names[1], author_names[0]])


def calc_h_index(citations):
    """
    Calculates the h-index from a list of citations.

    Inputs
    -------
        :citations: (list of ints) list of citations for each paper.

    Outputs
    -------
        :h_index: (int) h-index.
    """
    citations.sort()
    h_index = 0
    while True:
        H_citations = citations[citations >= h_index]

        # is this valid? For h index of N, I need at least N papers with N citations. H_ciations is the list of papers with them.
        if len(H_citations) >= h_index:
            pass
        else:
            h_index -= 1
            break

        h_index += 1
    return h_index

if __name__ == "__main__":
    api_key = sys.argv[1]
    author_id = 'e6T8gFsAAAAJ'
    time.sleep(random.uniform(3, 9))  # Sleep between 5 to 15 seconds. try to avoid getting blocked by google lol

    # try:
    paper_dict,  n_citations, h_index, n_first_author_citations, first_author_h_index = get_scrape_google_scholar(author_id, api_key)
    # except requests.Timeout as err:
    #     print("Timeout error")
    #     print(err)
    #     time.sleep(60)
    #     paper_dict = get_scrape_google_scholar(name)

    with open("data/google_scholar_scrape.json", "w") as f:
        json.dump(paper_dict, f, sort_keys=True, indent=2, separators=(",", ": "))
    np.savetxt("data/n_citations.txt", [n_citations])
    np.savetxt("data/h_index.txt", [h_index])
    np.savetxt("data/n_first_author_citations.txt", [n_first_author_citations])
    np.savetxt("data/first_author_h_index.txt", [first_author_h_index])

    
    today = datetime.now(ZoneInfo("America/New_York")).strftime("%m.%d.%Y")
    np.savetxt("data/last_updated.txt", [today], fmt="%s")
