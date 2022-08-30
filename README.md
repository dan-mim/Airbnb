# Airbnb
The aim of these script is to scrabe Airbnb.com and find the location of all parisian accomodations

## Classical methods
- airBnB_Selenium_Firefox.py uses Selenium to find the links of 300 accomodations and scrape their location.
- airBnB_chrome_threading_headless.py uses Selenium with Chrome in headless mode. This script could be used with google collab or with online servers that help it run faster to colect a lot of location data.
So far these script (on my local computer) can access 10 accomodation/minute. This is due to the use of Selenium.
That is why the folder requests_html should be inspected.

## Requests_html
The folder Requests_html gathers several technics that appear to be way more efficient in term of time optimisation.

# Log_in BNB:
For some use, it can be useful to login to a bnb account. For example to get some data about users.
This can be done thanks to the code in the folder log_in_bnb.
