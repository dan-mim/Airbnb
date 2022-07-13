# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 11:13:21 2022

@author: daniel.mimouni
"""

import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
import pandas as pd
import numpy as np 
import time
from selenium import webdriver
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
    WebDriverWait(browser, 7).until(EC.presence_of_element_located((By.XPATH, xp_icone_room)))
    lnks = browser.find_elements(By.TAG_NAME, "a")
    list_href = [lk.get_attribute('href') for lk in lnks if "https://www.airbnb.fr/rooms" in lk.get_attribute('href')]
    return(list(set(list_href)))

#% trouver tous les URL
def find_all_url():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome('chromedriver', options=chrome_options)
    url0 = "https://www.airbnb.fr/s/Paris--France/homes?adults=1&place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&refinement_paths%5B%5D=%2Fhomes&checkin=2022-10-10&checkout=2022-10-13"
    open_result(browser, url0)
    # trouve le nb de pages :
    xp_last_page = '//a[@class="_833p2h"]' 
    last_page_l = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xp_last_page)))
    last_page_l = browser.find_elements(By.XPATH, xp_last_page)
    nb_pages = int([d.text for d in last_page_l][-1])
    close_cookies(browser)
    #% scraping de chaque url: je récupere les urls de tous les bnb
    list_url_bnb = []
    for i in range(nb_pages):
        xp_current_page = '//button[@aria-current="page"]' 
        page_nb = int(WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xp_current_page))).text)
        print('scraping for page: ', page_nb)
        a = scrape_url(browser)
        print('caractéristiques de a: ', len(a), a[0:2])
        list_url_bnb.extend(a)
        xp_next_page = '//a[@aria-label="Suivant"]'
        if i != nb_pages-1 :
            WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, xp_next_page))).click()
    return(list_url_bnb)


#% je récupère la localisation des bnb pour chaque url de la liste list_url_bnb
def scraping_bnb_accomodation(list_url_bnb):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome('chromedriver', options=chrome_options)
    l_resultat = []
    for i,url in enumerate(list_url_bnb):
        open_result(browser, url) 
        # il faut scroller plusieurs fois en bas de la page pour faire charger d'autres balises
        for _ in range(4):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
        xp_map = '//div[@class="_384m8u"]' 
        ### Si l'element n'est toujours pas chargé on ne veut pas une erreur: on réessaie
        try:
            element = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xp_map)))
            element.location_once_scrolled_into_view
        except TimeoutException:
            print('exception passée pour url n° ', i)
            for _ in range(4):
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
                browser.execute_script("window.scrollTo(0, 3700)") 
            element = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xp_map)))
            element.location_once_scrolled_into_view
        xpath_coordinate = "/html/body/div[5]/div/div/div[1]/div/div/div[1]/div/div/div/div/div[1]/main/div/div[1]/div[5]/div/div/div/div[2]/div/section/div[3]/div[3]/div[2]/div/div/div[14]/div/a"
        lnks = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xpath_coordinate)))
        localisation = lnks.get_attribute('href').split('=')[1].replace('&z', '')
        l_resultat.append(localisation)
    return(l_resultat)

def slice_liste(liste, k):
    """
    Parameters
    liste : TYPE list
        DESCRIPTION. ' une liste de n éléments qu'on va slicer en k éléments 
    k : 
        TYPE entier

    exemple: a = [1, 2, 3, 4, 5, 6, 7, 6, 5, 4]
    slice_liste(a,4) --> [[1, 2, 3, 4], [5, 6, 7, 6], [5, 4]]
    slice_liste(a,2) --> [[1, 2], [3, 4], [5, 6], [7, 6], [5, 4]]
    -------
    """
    n = len(liste)
    new_l = []
    for i in range(n//k):
        new_l.append(liste[i*k:(i+1)*k])
    b = liste[(i+1)*k:]
    if b != []:
        new_l.append(b)
    return(new_l)

#% threading
def threading_bnb(list_url_bnb, k):
    """
    k est un entier qui réfère à la fonction slice_liste (se référer à sa descritpion
    """
    with ThreadPoolExecutor() as executor:
        # submit tasks and process results
        liste_loca = []
        i = 0
        for res in executor.map(scraping_bnb_accomodation, slice_liste(list_url_bnb, k)) :
            liste_loca.extend(res)
            print('#'*30, 'done for k = ', k)
            i = i + 1
    return(liste_loca) 

#%% Execution
list_url_bnb = find_all_url()
list_location = threading_bnb(list_url_bnb[:60], k)

#%% Travail pour trouver le nombre de threading en parallèle le plus efficace
list_temps = []
# liste des diviseurs de k
liste_k = [1, 2, 3, 4, 5, 6, 10, 12] #, 15, 20, 30, 60]
for k in liste_k[::-1]:
    print('#'*20,' pour k = ' , k)
    start = time.time()
    list_location = threading_bnb(list_url_bnb[:60], k)
    end = time.time()
    temps_execution = np.round((end-start)/60, 2)
    list_temps.append(temps_execution)
    print("~"*20, " le script s'est executé en ", temps_execution , ' minutes pour k = ', k)

tps_execution = pd.DataFrame({'k': liste_k, "temps d'execution": list_temps})