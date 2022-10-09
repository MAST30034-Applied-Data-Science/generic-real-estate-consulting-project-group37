# Generic Real Estate Consulting Project
Group 37

Members: Renhao Wu, Shiqi Liu, Zixuan Xiao 


# Project objective
This project aims to forecast the rental prices of properties throughout Victoria, Australia, and then figure out where they are most likely to increase in the next 3 years.
 
Meantime, by anaylsing the data, the project investigates what features are essential on rental prices.  

Finally, based on the results, we give recommendations for the most affordable and liveable suburbs.

# Dependencies
To install all the required packages and libraries, please refer to the text file `requirements.txt`

# Instructions
To run the pipeline, please visit the scripts directory and run the files in order:

1.`scrape.py`: This downloads the scraped rental properties data from https://www.domain.com.au/

2.`URL.ipynb`: This downloads the SA2 distinct boundaries, population data and weekly personal income by SA2 distincts  from https://www.abs.gov.au/

3.`visualization.ipynb`: This visualizes the geolocation of the scraped properties on map.

4.`properties.ipynb`: This preprocesses the scraped property data.

5.`population_pred.ipynb`: This forecasts the future population data.

6.`postcode.ipynb`: This implements the conversion of SA2 into postcode and add those census data into property data.

7.`sprint3.ipynb` : This uses Open Route Service API to get the geospatial data for each property and visualizes them on map.(NOTE: API keys are hidden, needed to get from https://api.openrouteservice.org/)

8.`sprint4.ipynb` : This applies EDA, Feature Engineering & Feature Analysis to the data and then builds the prediction model.

# Summary
The notebook `summary.ipynb` summarises the overall procedure of the project, including what features used, what models fitted, and what results achieved.

It also contains our finding and answers with regards to the project objective, with reasonable assumptions and any limitations and difficulties encountered.
