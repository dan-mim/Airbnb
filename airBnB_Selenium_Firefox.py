# -*- coding: utf-8 -*-
"""
Created on Sun Jul 10 13:42:00 2022

@author: daniel.mimouni

Dans ce script je scrape les localisation d'Airbnbs à Paris en utilisant Slenium avec Firefox
"""

#%% IMPORTATION des bibliothèques
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager #si j'utilise Firefox
from selenium.webdriver.firefox.options import Options # pour rajouter des options (comme ne pas montrer les fenetres firefox)
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import numpy as np 
import time
#relatif au temps d'attente :
from selenium.webdriver.support.wait import WebDriverWait
#from selenium.webdriver.common.by import By
from functools import partial 
############# pour ajuster les prix :
#############from selenium.webdriver.support import expected_conditions as EC
#############from selenium.webdriver import ActionChains
import string
#pour executer des codes en parallèle
from concurrent.futures import ThreadPoolExecutor

import os
import psutil # pour avoir accès à la mémoire vive utilisée

#% FONCTIONS
#% FERMER LES COOKIES
def close_cookies(browser):
    accept_cookies_xpath = "/html/body/div[5]/div/div/div[1]/div/div/div[2]/section/div[2]/div[2]/button"
    try:
       browser.find_element_by_xpath(accept_cookies_xpath).click()
    except NoSuchElementException:
       pass
   
#% OUVERTURE DE LA PAGE WEB
def open_result(browser, url):
    try:
        browser.get(url)
        close_cookies(browser)
    except:
        pass

#% scraping ul des logements bnb d'une page
def scrape_url(browser):
    lnks = browser.find_elements_by_tag_name("a")
    list_href = [lk.get_attribute('href') for lk in lnks if "https://www.airbnb.fr/rooms" in lk.get_attribute('href')]
    return(list(set(list_href)))

#% scraping des localisation de chaque airbnb
def scrape_loca(browser):
    lnks = browser.find_elements_by_tag_name("a")
    list_href = [lk.get_attribute('href') for lk in lnks if "https://maps.google.com/maps" in lk.get_attribute('href')]
    localisation = list_href[0].split('=')[1].replace('&z', '')
    return(localisation)

#% trouver tous les URL
def find_all_url():
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())#, options=option_browser)
    url0 = "https://www.airbnb.fr/s/Paris--France/homes?adults=1&place_id=ChIJD7fiBh9u5kcRYJSMaMOCCwQ&refinement_paths%5B%5D=%2Fhomes&checkin=2022-10-10&checkout=2022-10-13"
    open_result(browser, url0)
    # trouve le nb de pages :
    xp_last_page = '//a[@class="_833p2h"]' 
    last_page_l = browser.find_elements_by_xpath(xp_last_page)
    nb_pages = int([d.text for d in last_page_l][-1])
    time.sleep(5)
    close_cookies(browser)
    #% scraping de chaque url: je récupere les urls de tous les bnb
    list_url_bnb = []
    for i in range(nb_pages-1):
        a = scrape_url(browser)
        list_url_bnb.extend(a)
        xp_current_page = '//button[@aria-current="page"]' 
        print('scraped for page: ',[int(page.text) for page in browser.find_elements_by_xpath(xp_current_page)])
        xp_next_page = '//a[@aria-label="Suivant"]' 
        browser.find_elements_by_xpath(xp_next_page)[0].click()
        time.sleep(5)
    return(list_url_bnb)


#% je récupère la localisation des bnb pour chaque url
def scraping_bnb_accomodation(l_url):
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())#, options=option_browser)
    l_resultat = []
    for url in l_url:
        open_result(browser, url) 
        y = 0
        try:
            time.sleep(2)
            # to scroll down the page: it speeds the loading
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            resultat = scrape_loca()
        except:
            y = 2
            while y > 1 :
                    time.sleep(2)
                    # I scroll until I see the map :
                    try:
                        xp_map = '//div[@class="_384m8u"]' 
                        element = browser.find_elements_by_xpath(xp_map)
                        element[0].location_once_scrolled_into_view
                    # the map is visible and charge now
                    except:
                        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    close_cookies(browser)
                    #print((y-1)*2, " secondes pour l'url ", url)
                    try:
                        resultat = scrape_loca(browser)
                        y = 0
                    except:
                        y = y + 1
        l_resultat.append(resultat)
    browser.close()
    browser.quit()
    return(l_resultat)

def slice_liste(liste, k):
    """
    ----------
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
#%% EXECUTION
list_url_bnb = find_all_url()
list_ocation = threading_bnb(list_url_bnb[:30], 10)

#%% Recherche du meilleur paquet
list_temps = []
for k in range(10,31):
    start = time.time()
    list_ocation = threading_bnb(list_url_bnb[:30], k)
    end = time.time()
    temps_execution = np.round(end-start, 2)
    list_temps.append(temps_execution)
    print("~"*30)
    print("le script s'est executé en ", temps_execution , ' secondes')

tps_execution = pd.DataFrame({'k':[k for k in range(11,31)] , "temps d'execution":list_temps})












