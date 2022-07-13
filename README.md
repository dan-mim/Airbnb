# Airbnb
The aim of these script is to scrabe Airbnb.com and find the location of all parisian accomodations

airBnB_Selenium_Firefox.py uses Selenium to find the links of 300 accomodations and scrape their location.
airBnB_chrome_threading_headless.py uses Selenium with Chrome in headless mode. This script could be used with google collab or with online servers that help it run faster to colect a lot of location data.
So far these script (on my local computer) can access 10 accomodation/minute. This is due to the use of Selenium. Therfore I will try using Scrapy to rise this ratio.
