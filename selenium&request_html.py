# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 11:05:38 2022

@author: daniel.mimouni
"""


# import sys
# sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
import pandas as pd
import numpy as np 
import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests_html import HTMLSession

#%% Fonction pretraitement data
# obtention des url0 : la carte de l'IDF est découpé en un certain nb de zone 
# définies dans tab_lat_long et on scrapera les résultats de ces urls (ces carrés 1 à 1)
def create_url0(i):
    """
    retourne le ie url correspondant au carré
    """
    tab_lat_long = pd.read_csv('tab_lat_long.csv', delimiter=';')
    liste_url0 = []
    for i in range(tab_lat_long.shape[0]):
        x_max = tab_lat_long.iloc[i].x_max
        x_min = tab_lat_long.iloc[i].x_min
        y_max = tab_lat_long.iloc[i].y_max
        y_min = tab_lat_long.iloc[i].y_min
        url = f'https://www.airbnb.fr/s/homes?ne_lat={y_max}&ne_lng={x_max}&sw_lat={y_min}&sw_lng={x_min}'
        liste_url0.append(url)
    return(liste_url0[i])

#%% Fonctions scraping
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

#scrape les données de chaques Airbnb de la page
def scraping_donnees_airbnb(url):
    donnees_airbnb = pd.DataFrame()
    session = HTMLSession()
    r = session.get(url)
    html_str = r.text
    # with open('html_str_2.json', 'w', encoding='utf-8') as f:
    #     f.write(html_str)
    list_of_words = html_str.replace(',', ':').replace(' ', ':').split(':')
    try:
        #indices des airbnb (permet de retrouver leur url)
        indices_airbnb_id = [i-1 for i, x in enumerate(list_of_words) if x == '"isNewListing"']
        l_airbnb_id = [int(list_of_words[i].replace('"', ''))  for i in indices_airbnb_id]
        #coordonnées géographiques
        indices_lat = [i+1 for i, x in enumerate(list_of_words) if x == '"lat"']
        l_lat = [float(list_of_words[i]) for i in indices_lat]
        indices_lng = [i+1 for i, x in enumerate(list_of_words) if x == '"lng"']
        l_lng = [float(list_of_words[i]) for i in indices_lng]
        #nb d'ocupaants possibles
        indices_nb_voyageurs = [i+1 for i, x in enumerate(list_of_words) if x == '"personCapacity"']
        l_nb_voyageurs = [int(list_of_words[i].replace('"', '')) for i in indices_nb_voyageurs]
        #prix
        indices_prix = [i-1 for i, x in enumerate(list_of_words) if x == '"qualifier"']
        l_prix = [float(list_of_words[i].replace('"', '')[:-2]) for i in indices_prix]
        # Je remplie le DataFrame:
        donnees_airbnb['indice_bnb'] = l_airbnb_id
        donnees_airbnb['latitude'] = l_lat
        donnees_airbnb['longitude'] = l_lng
        donnees_airbnb['nb_voyageurs'] = l_nb_voyageurs
        donnees_airbnb['prix'] = l_prix 
    except:
        pass
    return(donnees_airbnb.drop_duplicates())

#% trouver tous les URL
def find_all_data(browser, carre_nb, prix_1, prix_2):
    url0 = create_url0(carre_nb) + f'&price_min={prix_1}&price_max={prix_2}' #&search_type=filter_change'
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
    #% scraping de chaque url: je récupere les données de tous les bnb
    all_donnees_airbnb = pd.DataFrame()
    for i in range(nb_pages):
        if nb_pages > 1:
            xp_current_page = '//button[@aria-current="page"]' 
            page_nb = int(WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xp_current_page))).text)
            print('scraping for page: ', page_nb)
        # je récupère l'url de la page puis je scrape la page
        url = browser.current_url
        #print(url)
        donnees_airbnb = scraping_donnees_airbnb(url)
        #je concatène les données scrapée au dataframe all_donnees_airbnb
        all_donnees_airbnb = pd.concat([all_donnees_airbnb, donnees_airbnb])
        xp_next_page = '//a[@aria-label="Suivant"]'
        if i != nb_pages-1 :
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, xp_next_page))).click()
    return(all_donnees_airbnb)

def main_selenium(carre_nb, prix_min, prix_max, step=1):
    all_all_donnees_airbnb = pd.DataFrame()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    for prix_1 in range(prix_min, prix_max, step):
        print('='*45, 'avancement : prix = ', prix_1, "€") #permet de juger l'avancement
        prix_2 = prix_1 + step
        #résulat :
        all_donnees_airbnb = find_all_data(browser, carre_nb, prix_1, prix_2)
        #archivage
        if not os.path.exists(f'carre_n_{carre_nb}_all_donnees_airbnb'):
            os.makedirs(f'carre_n_{carre_nb}_all_donnees_airbnb')
        all_donnees_airbnb.to_csv(f'carre_n_{carre_nb}_all_donnees_airbnb/data_{prix_1}_to_{prix_2}.csv')
        all_all_donnees_airbnb = pd.concat([all_all_donnees_airbnb, all_donnees_airbnb])
    browser.close()
    browser.quit()
    return(all_all_donnees_airbnb)

#%% EXECUTION
start = time.time()
for nb_carres in range(0,17):
    if nb_carres not in [5,9]: #les zones 5 et 9 sont plus denses donc on va adapter le maillage des prix
        all_all_donnees_airbnb1 = main_selenium(nb_carres, 0,  180,  30)
        all_all_donnees_airbnb2 = main_selenium(nb_carres, 180, 880,  50)
        all_all_donnees_airbnb3 = main_selenium(nb_carres, 880, 1000,  120)
        # all_all_donnees_airbnb4 = main_selenium(nb_carres, 900, 1000, 100)
end = time.time()
temps_execution_1 = np.round((end-start)/60, 2)
print("~"*20, " le script s'est executé en ", temps_execution_1 , ' minutes')

#%% Posttraitement:
#cette fonction concatène tous les .csv résultats des différents fichiers
def concat_all():
    folders = [f for f in os.listdir() if f[0:7]=='carre_n']
    all_data = pd.DataFrame()
    for folder in folders:
        files = os.listdir(f'{folder}')
        for file in files:
            data = pd.read_csv(f'{folder}/{file}', index_col=None, header=0)
            all_data = pd.concat([all_data, data])
    return(all_data)








