"""
Module to scrape google scholar information. Inspired by dfm/cv/update-astro-pubs

author: @arjunsavel
"""
import inspect
import json
import os
import pdb
import random
import time

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


def get_scrape_google_scholar(author):
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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }

    # url = f"""https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={author.replace(' ', '+')}&pagesize=80"""
    url = "https://scholar.google.com/citations?user=e6T8gFsAAAAJ&hl=en&oi=ao&cstart=0&pagesize=80"
    session = requests.Session()
    # response = session.get(url, headers=get_headers())
    # # response = requests.post(url, headers=headers)
    # if response.status_code != 200:
    #     print(response.text[:500])
    # soup = BeautifulSoup(response.content, "html.parser")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # Optionally add proxy settings to the WebDriver if you plan to use proxies
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find_all("table")
    print(table)

    title_list = table[1].findAll("a", class_="gsc_a_at")
    title_list = [t.text for t in title_list]

    rest_info = table[1].findAll("div", class_="gs_gray")
    rest_info = [r.text for r in rest_info]
    authors_list = rest_info[::2]
    pub_info = rest_info[1::2]

    pub_years = table[1].findAll("span", class_="gs_oph")
    pub_years = [p.text for p in pub_years]

    citations = table[1].findAll("a", class_="gsc_a_ac gs_ibl")
    citations_list = [c.text for c in citations]

    citations = []
    cleaned_articles = []
    for i, title in enumerate(title_list):
        cleaned_article = {}
        citation = citations_list[i]
        citation = clean_citation(citation)

        citations += [citation]
        journal_info = pub_info[i]
        if journal_info == "":
            continue
        journal_info = clean_journal_info(journal_info)

        cleaned_article["citations"] = citation

        cleaned_article["title"] = title

        authors = authors_list[i]
        cleaned_article["authors"] = clean_authors(authors)



        cleaned_article["journal"] = journal_info["journal"]
        cleaned_article["page"] = journal_info["page"]
        cleaned_article["volume"] = journal_info["volume"]
        cleaned_article["arxiv"] = journal_info["arxiv"]

        cleaned_article["year"] = pub_years[i]

        cleaned_article["url"] = None
        cleaned_article["doi"] = None
        cleaned_article["pubdate"] = None

        # todo: OSF!
        # todo: get this in the preprint checking func :)
        if cleaned_article["journal"] == "PsyArXiv":
            cleaned_article["doctype"] = "eprint"
        else:
            cleaned_article["doctype"] = "article"

        cleaned_articles += [cleaned_article]

    citations.sort()

    citations = np.array(citations)
    # pdb.set_trace()
    # citations[citations==6] = 7
    h_index = calc_h_index(citations)
    # h_index = np.arange(len(citations))[np.arange(len(citations)) > citations[::-1]][0]
    first_author_pubs = [a for a in cleaned_articles if author in a["authors"][0]]
    first_author_citations = np.array([a["citations"] for a in first_author_pubs])
    n_first_author_citations = np.sum(first_author_citations)

    first_author_citations.sort()
    first_author_h_index = calc_h_index(first_author_citations)
    print(h_index)
    # pdb.set_trace()
    n_citations = np.sum(citations)
    print(n_citations)
    return cleaned_articles, n_citations, h_index, n_first_author_citations, first_author_h_index


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

    name = "McDanal, R"
    time.sleep(random.uniform(3, 9))  # Sleep between 5 to 15 seconds. try to avoid getting blocked by google lol

    try:
        paper_dict,  n_citations, h_index, n_first_author_citations, first_author_h_index = get_scrape_google_scholar(name)
    except requests.Timeout as err:
        print("Timeout error")
        print(err)
        time.sleep(60)
        paper_dict = get_scrape_google_scholar(name)

    with open("data/google_scholar_scrape.json", "w") as f:
        json.dump(paper_dict, f, sort_keys=True, indent=2, separators=(",", ": "))
    np.savetxt("data/n_citations.txt", [n_citations])
    np.savetxt("data/h_index.txt", [h_index])
    np.savetxt("data/n_first_author_citations.txt", [n_first_author_citations])
    np.savetxt("data/first_author_h_index.txt", [first_author_h_index])
