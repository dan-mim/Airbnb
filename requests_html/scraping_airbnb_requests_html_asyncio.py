# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 17:29:27 2022

@author: daniel.mimouni
Unefois que j'ai tous les liens des AirBnbs je peux retrouver les informations qu'il me faut
grâce à requests_html.
En utilisant Asyncio mon programme s'execute en 9 fois moins de temps ! 
"""
import time
import numpy as np
import pandas as pd
import os
import random
from requests_html import AsyncHTMLSession
import asyncio

async def work(session, url):
    time.sleep(random.randrange(1, 4))
    r = await session.get(url)
    html_str = r.text
    list_of_words = html_str.replace(',', ':').replace(' ', ':').split(':')
    try:
        airbnb_id = list_of_words[list_of_words.index('"id"') + 1]
        latitude = list_of_words[list_of_words.index('"lat"') + 1]
        longitude = list_of_words[list_of_words.index('"lng"') + 1]
        nb_voyageurs = list_of_words[list_of_words.index('voyageurs"}') - 1].replace('"', '')
        prix = list_of_words[list_of_words.index('€.') - 1]
        lat_long_nb_voyageurs_prix = [float(latitude), float(longitude), int(nb_voyageurs), float(prix)]
    except:
        lat_long_nb_voyageurs_prix = []
    return(lat_long_nb_voyageurs_prix)

async def main(list_url_bnb):
    session = AsyncHTMLSession()
    tasks = (work(session, url) for url in list_url_bnb)
    return await asyncio.gather(*tasks)
# ###ajout
# async def scraping_all_url():
#     list_url_bnb = []
#     for doc in os.listdir('url_bnb'):
#         list_url_bnb.append(list(pd.read_csv(f"url_bnb/{doc}").url_bnb))
#     task = (main(liste_) for liste_ in list_url_bnb)
#     return await asyncio.gather(*task)
    #liste_lat_long = asyncio.run(main(list_url_bnb)) # ou await main(list_url_bnb) si une boucle tourne toujours

###ajout    

# start = time.time()
### list_url_bnb = list(pd.read_csv("list_url_bnb.csv").liste_url_bnb)
#liste_lat_long = asyncio.run(main(list_url_bnb)) # ou await main(list_url_bnb) si une boucle tourne toujours
#liste_res = asyncio.run(scraping_all_url())
# end = time.time()
# temps_execution_1 = np.round((end-start)/60, 2)
# print("~"*20, " le script s'est executé en ", temps_execution_1 , ' minutes')

#%% TEST 1: je construis une grande liste et j'execute main
start = time.time()
list_url_bnb_2 = []
for doc in os.listdir('url_bnb'):
    list_url_bnb_2.extend(list(pd.read_csv(f"url_bnb/{doc}").url_bnb))
list_url_bnb_2 = list(set(list_url_bnb_2))
liste_extraction = await main(list_url_bnb_2)
end = time.time()
temps_execution_1 = np.round((end-start)/60, 2)
print("~"*20, " le script s'est executé en ", temps_execution_1 , ' minutes')
print('len(list_url_bnb_2) = ', len(list_url_bnb_2))
print('len(liste_extraction) = ', len(liste_extraction))
# #%% TEST 2 : j'execute scraping_all_url qui divise en tache des sous listes
# start = time.time()
# liste_res_extraction = await scraping_all_url()
# end = time.time()
# temps_execution_1 = np.round((end-start)/60, 2)
# print("~"*20, " le script s'est executé en ", temps_execution_1 , ' minutes')

# acc = 0
# for i in range(len(os.listdir('url_bnb'))): 
#     acc = acc + len(liste_res_extraction[i])
# print('acc = ', acc)

#%%
long = []
lat = []
nb_voyageurs = []
prix = []
for data in liste_extraction:
    if data != []:
        lat.append(data[0])
        long.append(data[1])
        nb_voyageurs.append(data[2])
        prix.append(data[3])
    
resultats = pd.DataFrame({"latitude": lat, "longitude":long, "nb_voyageurs": nb_voyageurs, "prix" : prix})
resultats.to_csv('resultats_airbnb.csv')
#resultats.to_excel('resultats_airbnb.xlsx')
#%%
import geoplotlib
from geoplotlib.utils import read_csv, BoundingBox, DataAccessObject
import pandas as pd

df = pd.read_csv('resultats_airbnb.csv').drop('Unnamed: 0', axis=1)
df.columns = ['lat', 'lon', 'nb_voyageurs'] #,'Population in 2011']
#geoplotlib.hist(df, colorscale='sqrt', binsize=8)
# geoplotlib.kde(df, bw=7, cut_below=1e-4)
#geoplotlib.dot(df)

geoplotlib.set_bbox(BoundingBox.from_nominatim('ILE-DE-FRANCE'))
geoplotlib.show()




