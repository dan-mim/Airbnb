## Get the links and then scrape them one by one
- function_selenium_airbnb.py : This function collects the links of the airbnb accomodations in a region. Here the region to be collected is set to Paris. The function uses filter in the airbnb general page in order to get all the airbnbs. To put it differently: the bot sets the filters to different ranges of price from 0 to 1000€/night to get the maximum number of airbnb without reaching the threashold of 300 accomodation by research
- scraping_airbnb_requests_html_asyncio.py : This script uses the links that can be obtained thanks to function_selenium_airbnb.py: 1 link = 1 accomodation. This script can handle more than 2000 links /minute and scrape the locations, price and number of beds.

## Scrape directly everything with selenium and requests_html
This scrpit is the most efficient of the repository.
It can be adapted so that only a city is scraped for example.
- tab_lat_long.csv : L'Ile de France is divided into areas(squares). This documents are the latitudes and longitudes of the squares.
- selenium&request_html.py : This script uses tab_lat_long.csv. because it scrapes the airbnb of each areas. For each areas the airbnbs are filtered thanks to a price range and for each price range the location, number of travelers, price and id of the bnb are scraped directly in the research page! There is no need to acceed each accomodation website, which skyrockets the time gains.

## The folder final_version is ready to be used
