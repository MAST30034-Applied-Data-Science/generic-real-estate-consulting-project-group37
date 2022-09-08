"""
A very simple and basic web scraping script. Feel free to
use this as a source of inspiration, but, make sure to attribute
it if you do so.

This is by no means production code.
"""
# built-in imports
import re
import requests
import numpy as np
from json import dump
from ast import excepthandler
from collections import defaultdict

# user packages
from bs4 import BeautifulSoup
from urllib.request import urlopen

# constants
BASE_URL = "https://www.domain.com.au"
N_PAGES = range(1, 51) # maximum 50 pages
headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0)"
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
# begin code
url_links = []
property_metadata = defaultdict(dict)



# generate list of urls to visit
for page in N_PAGES:
    #change ptype=house/apartment/town-house to get properties of these three types
    url = BASE_URL + f"/rent/?ptype=town-house&sort=default-desc&state=vic&page={page}"  
    bs_object = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")


    # find the unordered list (ul) elements which are the results, then
    # find all href (a) tags that are from the base_url website.
    index_links = bs_object \
        .find(
            "ul",
            {"data-testid": "results"}
        ) \
        .findAll(
            "a",
            href=re.compile(f"{BASE_URL}/*") # the `*` denotes wildcard any
        )

    for link in index_links:
        # if its a property address, add it to the list
        if 'address' in link['class']:
            url_links.append(link['href'])


# for each url, scrape some basic metadata

for property_url in url_links[1:]:
    bs_object = BeautifulSoup(requests.get(property_url, headers=headers).text, "html.parser")

    # looks for the header class to get property name
    property_metadata[property_url]['name'] = bs_object \
        .find("h1", {"class": "css-164r41r"}) \
        .text

    # looks for the div containing a summary title for cost
    property_metadata[property_url]['cost_text'] = bs_object \
        .find("div", {"data-testid": "listing-details__summary-title"}) \
        .text

    # extract coordinates from the hyperlink provided
    property_metadata[property_url]['coordinates'] = [
        float(coord) for coord in re.findall(
            r'destination=([-\s,\d\.]+)', # use regex101.com here if you need to
            bs_object \
                .find(
                    "a",
                    {"target": "_blank", 'rel': "noopener noreferer"}
                ) \
                .attrs['href']
        )[0].split(',')
    ]

    #extract number of beds, number of bathrooms and number of parking
    property_metadata[property_url]['rooms'] = [
        re.findall(r'\d\s[A-Za-z]+', feature.text) for feature in bs_object \
            .find("div", {"data-testid": "property-features"}) \
            .findAll("span", {"data-testid": "property-features-text-container"})
    ]

    #extract internal area (in m^2) 
    try:
        property_metadata[property_url]['area'] = re \
            .search(r"\d+",bs_object \
            .find("div", {"data-testid": "strip-content-list"}) \
            .find("span").text) \
            .group()
    except:
        property_metadata[property_url]['area'] = np.NaN


    #extract property type
    try:
        property_metadata[property_url]['type'] = bs_object \
                .find("div",{"data-testid": "listing-summary-property-type"}) \
                .find("span") \
                .text
    except:
        property_metadata[property_url]['type'] = np.NaN

    #extract rental bond($)
    try:
        property_metadata[property_url]["bond"] = re \
            .search(r"\d+",bs_object \
            .find("div",{"data-testid":"strip-content-list"}) \
            .findAll("li")[1].text) \
            .group()
    except :
        property_metadata[property_url]["bond"] = np.NaN

    #extract property features
    property_metadata[property_url]['features'] = [
        feature.text for feature in bs_object \
            .findAll("li",{"data-testid": "listing-details__additional-features-listing"}) \
    ]
  
    #extract property description
    property_metadata[property_url]['desc'] = re \
        .sub(r'<br\/>', '\n', str(bs_object.find("p"))) \
        .strip('</p>')



# output to example json in data/raw/
with open('../data/raw/town_house.json', 'w') as f:
    dump(property_metadata, f)