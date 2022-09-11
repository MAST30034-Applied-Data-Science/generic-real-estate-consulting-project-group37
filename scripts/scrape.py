#modified the skeleton code provided

# built-in imports
import re
import requests
import numpy as np
import pandas as pd
from json import dump
from ast import excepthandler
from collections import defaultdict

# user packages
from bs4 import BeautifulSoup
from urllib.request import urlopen

#create a dataframe to store url links for each postcode
postcode_urls = pd.DataFrame(columns=['postcode','url_links'])
BASE_URL = "https://www.domain.com.au"
headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0)"
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}

#VIC postcodes are from 3000 to 4000
postcodes = range(3000,4000)

for postcode in postcodes:
    url_links = []
    postcode_url = f"https://www.domain.com.au/rent/?postcode={postcode}&ssubs=0&sort=default-desc"
    postcode_bs = BeautifulSoup(requests.get(postcode_url, headers=headers).text, "html.parser")

    #get number of rental properties for each postcode
    num_results = int(re \
        .search(r'\d+',postcode_bs \
        .find('h1',{"data-testid":"summary"}) \
        .find("strong").text) \
        .group()
        )
    #check if it has results, and calculate the corresponding pages it needed to display
    #one page can only display 20 results
    if num_results != 0:
        if num_results % 20 == 0:
            N_PAGES = range(1,num_results//20 + 1)        
        else:
            N_PAGES = range(1,num_results//20 + 2)
        
        #generate list of urls to visit for each postcode
        for page in N_PAGES:
            url = postcode_url + f"&page={page}"  
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

        #store list of urls with corresponding postcode into the dataframe
        postcode_urls.loc[len(postcode_urls)] = [postcode,url_links]



# for each url of each postcode, scrape some basic metadata
property_metadata = defaultdict(dict)
for i in range(len(postcode_urls)):
    
    for property_url in postcode_urls["url_links"][i][:]: 
        bs_object = BeautifulSoup(requests.get(property_url, headers=headers).text, "html.parser")

        #check if the page has valid information
        if bs_object.find("h1", {"class": "css-164r41r"}):
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
                    r'destination=([-\s,\d\.]+)', 
                    bs_object \
                        .find(
                            "a",
                            {"target": "_blank", 'rel': "noopener noreferer"}
                        ) \
                        .attrs['href']
                )[0].split(',')
            ]

            #extract number of rooms, number of bathrooms and number of parking
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

            #extract unverified features
            property_metadata[property_url]["unverified_features"] = [
                unverified.text.replace("*","") for unverified in bs_object \
                    .findAll("li",{"data-testid": "listing-details__additional-features-suggested"}) \
            ]
            #extract property description
            property_metadata[property_url]['desc'] = [
                element.text for element in bs_object \
                    .find("div",{"data-testid": "listing-details__description"}) \
                    .findAll("p")
            ]



# output to properties metadata as json file in data/raw_data/
with open('../data/raw_data/properties.json', 'w') as f:
    dump(property_metadata, f)