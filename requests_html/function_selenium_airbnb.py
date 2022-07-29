# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 14:58:02 2022

@author: daniel.mimouni
"""


import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
import pandas as pd
import numpy as np 
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

#%% Fonctions
#% close cookies
def close_cookies(browser):
    accept_cookies_xpath = "/html/body/div[5]/div/div/div[1]/div/div/div[2]/section/div[2]/div[2]/button"
    try:
       browser.find_element(By.XPATH, accept_cookies_xpath).click()
    except NoSuchElementException:
       pass

#% open the web page for a url link
def open_result(browser, url):
    try:
        browser.get(url)
        close_cookies(browser)
    except:
        pass

#% scraping url des logements bnb d'une page
def scrape_url(browser):
    xp_icone_room = '//div[contains(@aria-labelledby,"title_")]'
    try:
        WebDriverWait(browser, 7).until(EC.presence_of_element_located((By.XPATH, xp_icone_room)))
    except:
        pass
    lnks = browser.find_elements(By.TAG_NAME, "a")
    list_href = [lk.get_attribute('href') for lk in lnks if "https://www.airbnb.fr/rooms" in lk.get_attribute('href')]
    return(list(set(list_href)))

#% trouver tous les URL
def find_all_url(browser, prix_1, prix_2):
    url0 = f'https://www.airbnb.fr/s/Paris/homes?price_min={prix_1}&price_max={prix_2}' #&search_type=filter_change'
    open_result(browser, url0)
    # trouve le nb de pages :
    xp_last_page = '//a[@class="_833p2h"]' 
    try:
        last_page_l = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xp_last_page)))
        last_page_l = browser.find_elements(By.XPATH, xp_last_page)
        nb_pages = int([d.text for d in last_page_l][-1])
    except TimeoutException:
        nb_pages = 1
    close_cookies(browser)
    #% scraping de chaque url: je récupere les urls de tous les bnb
    list_url_bnb = []
    for i in range(nb_pages):
        if nb_pages > 1:
            xp_current_page = '//button[@aria-current="page"]' 
            page_nb = int(WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xp_current_page))).text)
            print('scraping for page: ', page_nb)
        a = scrape_url(browser)
        print('^'*20, 'caractéristiques de a: ', len(a)) #, a[0:2])
        list_url_bnb.extend(a)
        xp_next_page = '//a[@aria-label="Suivant"]'
        if i != nb_pages-1 :
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, xp_next_page))).click()
    return(list_url_bnb)

def main_selenium(prix_min, prix_max, step=1):
    links = []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    for prix_1 in range(prix_min, prix_max, step):
        print('='*45, 'avancement : prix = ', prix_1, "€") #permet de juger l'avancement
        prix_2 = prix_1 + step
        #résulat :
        liste_url_bnb = find_all_url(browser, prix_1, prix_2)
        #archivage
        url_df = pd.DataFrame({'url_bnb':liste_url_bnb})
        url_df.to_csv(f'url_bnb/url_{prix_1}_to_{prix_2}.txt')
        links.extend(liste_url_bnb)
    browser.close()
    browser.quit()
    return(links)

#%% EXECUTION
start = time.time()
list_url_bnb = main_selenium(0,   30,   30)
list_url_bnb = main_selenium(30,  100,  2)
# list_url_bnb = main_selenium(100, 240,  5)
# list_url_bnb = main_selenium(240, 500,  20)
# list_url_bnb = main_selenium(500, 900,  40)
# list_url_bnb = main_selenium(900, 1000, 100)
end = time.time()
temps_execution_1 = np.round((end-start)/60, 2)
print("~"*20, " le script s'est executé en ", temps_execution_1 , ' minutes')
print('len(list_url_bnb) = ', len(list_url_bnb))

# l  = pd.DataFrame({'liste_url_bnb':list_url_bnb})
# l.to_csv("list_url_bnb.csv")












