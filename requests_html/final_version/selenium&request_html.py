# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 11:05:38 2022

@author: daniel.mimouni
"""

print("""
      Prérequis: 
          -Il faut qu'un document 'tab_lat_long.csv' soit dans le mêle répertoire que le code.
      Ce code a pour objectif de récupérr toutes les localisations (capacité et prix), des Airbnb en Ile de France.
      Pour cela il s'appuie sur le scraping de données en utilisant Selenium et Requests_html.
      Le code fonctionne en 6 étapes:
    1) Au préalable la carte de l'IDF est découpée en un certain nombre de carrés geographiques
    2) Les recherches se font geographiquement carré par carré: je parcours la liste des carrés et ils sont analysés  séparement comme requètes geographiques sur Airbnb
    3) Pour chaque requète géographique, je filtre par prix pas à pas car la limite d'affichage de Airbnb est de 300 logements pa recherche donc on ne veut pas dépasser cette limite.
    4) Une fois qu'on a fait une requète géographique + une requète par prix (via filtrage), on enrregistre l'url de la page en cours et on ouvre virtuellement cette url avec requests_html (on crée une 'session')
    On passe alors à la page suivant de la meme requete (georgpahie + filtrage prix mais page 2, puis 3, puis ... 15)
    5) Une fois la session ouverte, je scrape les données qui m'interessent. 
    remarque: avec requests_htm je n'ai pas beoin d'attendre le chargement de la page je récupère directement depuis le réseau.
    6) Je concatène les résultats page par page, puis plage de prix par plage de prix, puis carré par carré grâce à la fonction 'concat_all()'
      """
      
import pandas as pd
import numpy as np 
import os
import time
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests_html import HTMLSession

#%% Fonction pretraitement data
# obtention des url0 : la carte de l'IDF est découpé en un certain nb de zone 
# définies dans tab_lat_long et on scrapera les résultats de ces urls (ces carrés 1 à 1)
def create_url0(j):
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
    return(liste_url0[j])

#%% Fonctions scraping

def close_cookies(browser):
    """
    close cookies
    """
    accept_cookies_xpath = "/html/body/div[5]/div/div/div[1]/div/div/div[2]/section/div[2]/div[2]/button"
    try:
       browser.find_element(By.XPATH, accept_cookies_xpath).click()
    except NoSuchElementException:
       pass

def open_result(browser, url):
    """
    open the web page for a url link and close cookies
    """
    try:
        browser.get(url)
        close_cookies(browser)
    except:
        pass



def scraping_donnees_airbnb(url):
    """
    scrape les données de chaques Airbnb de la page
    pour 1 page de recherche correspondant à 1 géographie (1 carré) et 1 fourchette de prix,
    je scrape grace à requests_html les aractéristiques des rbnb directement depuis la réponse réseau:
    """
    #tableau de résultat pour 1 page
    donnees_airbnb = pd.DataFrame()
    #création de la session:
    session = HTMLSession()
    r = session.get(url)
    html_str = r.text
    #si la page ne comprend que des doubles voyages (1 voyage 2 logements)
    if 'Un voyage, deux logements' not in html_str and 'ExploreSplitStaysListingsSection' in html_str:
        html_str = ''
    #si la page comprend des logements ET des doubles logements
    if 'Un voyage, deux logements' in html_str:
        html_str = html_str.split('ExploreSplitStaysListingsSection')[0]
    #traitement du texte
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


def find_all_data(browser, carre_nb, prix_1, prix_2):
    """
    trouver tous les URL: pour 1 géographie (1 carré) et 1 fourchette de prix prix_1 à prix_2
    je récupère les url des pages résultats de rbnb et je les envoie à scraping_donnees_airbnb(url)
    """
    #construction de l'url
    url0 = create_url0(carre_nb) + f'&price_min={prix_1}&price_max={prix_2}' #&search_type=filter_change'
    open_result(browser, url0)
    # je trouve le nb de pages :
    xp_last_page = '//a[@class="_833p2h"]' 
    try:
        last_page_l = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xp_last_page)))
        last_page_l = browser.find_elements(By.XPATH, xp_last_page)
        nb_pages = int([d.text for d in last_page_l][-1])
    except TimeoutException:
        nb_pages = 1
    #je ferme les cookies
    close_cookies(browser)
    ## scraping de chaque url: je récupere les données de tous les bnb grçace à la fonction scraping_donnees_airbnb(url)
    all_donnees_airbnb = pd.DataFrame()
    #je parcours les pages:
    for i in range(nb_pages):
        if nb_pages > 1:
            xp_current_page = '//button[@aria-current="page"]' 
            page_nb = int(WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, xp_current_page))).text)
            print('scraping for page: ', page_nb)
        # je récupère l'url de la page puis je scrape la page
        url = browser.current_url
        print(f"l'url de la page {page_nb} est : ", url)
        #je scrape les données des airbnb pour cette page
        donnees_airbnb = scraping_donnees_airbnb(url)
        #je concatène les données scrapée au dataframe all_donnees_airbnb
        all_donnees_airbnb = pd.concat([all_donnees_airbnb, donnees_airbnb])
        #je change de page:
        xp_next_page = '//a[@aria-label="Suivant"]'
        if i != nb_pages-1 :
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, xp_next_page))).click()
        else:
            time.sleep(8)
    return(all_donnees_airbnb)

def main_selenium(carre_nb, prix_min, prix_max, step=1):
    """
    j'ouvre un driver/browser pour 1 carré une fourchette large et un pas particulier 
    puis je parcours les fourchette de prix : *pour chaque pas de prix j'appelle la fonction 'find_all_data' 
    qui parcourra les pages 1 à 1 et appelera à chaque fois la fonction de scrping des pages
    """
    all_all_donnees_airbnb = pd.DataFrame()
    firefox_options = Options()
    #mode headleas pour ne pas avoir des fenetres qui s'ouvrent
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=firefox_options)
    for prix_1 in range(prix_min, prix_max, step):
        print('='*45, 'avancement : prix = ', prix_1, "€") #permet de juger l'avancement
        prix_2 = prix_1 + step
        #résulat :
        all_donnees_airbnb = find_all_data(browser, carre_nb, prix_1, prix_2)
        #archivage: je crée un dossier par carré (si le dossier n'existe pas déjà: dans ce cas j'ecrase les données dedans)
        if not os.path.exists(f'carre_n_{carre_nb}_all_donnees_airbnb'):
            os.makedirs(f'carre_n_{carre_nb}_all_donnees_airbnb')
        all_donnees_airbnb.to_csv(f'carre_n_{carre_nb}_all_donnees_airbnb/data_{prix_1}_to_{prix_2}.csv')
        all_all_donnees_airbnb = pd.concat([all_all_donnees_airbnb, all_donnees_airbnb])
    browser.close()
    browser.quit()
    return(all_all_donnees_airbnb)

#%% EXECUTION
#Adapter ce bloc en fonction du nombre de carrés et de quels carrés correspondent à la zone dense de Paris.
start = time.time()
for nb_carres in range(4):
    if nb_carres not in [5,9]: #les zones 5 et 9 sont plus denses donc on va adapter le maillage des prix
        all_all_donnees_airbnb1 = main_selenium(nb_carres, 0,  180,  30)
        all_all_donnees_airbnb2 = main_selenium(nb_carres, 180, 880,  50)
        all_all_donnees_airbnb3 = main_selenium(nb_carres, 880, 1000,  120)
        all_all_donnees_airbnb4 = main_selenium(nb_carres, 900, 1000, 100)
    if nb_carres  in [5,9]: #les zones 5 et 9 sont plus denses donc on va adapter le maillage des prix
        all_all_donnees_airbnb1 = main_selenium(nb_carres, 0,  180,  10)
        all_all_donnees_airbnb2 = main_selenium(nb_carres, 180, 880,  35)
        all_all_donnees_airbnb3 = main_selenium(nb_carres, 880, 1000,  60)
        all_all_donnees_airbnb4 = main_selenium(nb_carres, 900, 1000, 100)    
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

concat_all().to_csv('resultat_final_bnb_daniel.csv')







