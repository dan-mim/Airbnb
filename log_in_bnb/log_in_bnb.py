# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 15:04:55 2022

@author: daniel.mimouni
"""

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

#%%

url = 'https://airbnb.com/users/show/156996131'
#entry data
email_adress = 'projets.dan@gmail.com'
password = 'A COMPLETER'
#function
chrome_options = webdriver.ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument('--disable-web-security')
#chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
open_result(browser, url)  
time.sleep(5) #the page charges
close_cookies(browser)
#save the main page handle
main_page = browser.current_window_handle
connect_with_google_XPATH = '//button[@aria-label="Continuer avec Facebook"]'
connect_with_google = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, connect_with_google_XPATH))).click()
# changing the handles to access login page
for handle in browser.window_handles:
    if handle != main_page:
        login_page = handle
          
# change the control to signin page        
browser.switch_to.window(login_page)
accept_cookies_xpath = '//button[@data-cookiebanner="accept_only_essential_button"]'
browser.find_element(By.XPATH, accept_cookies_xpath).click()

#enter mail
mail_input = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']" )))
passeword_input = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']" )))
mail_input.clear()
mail_input.send_keys(email_adress)
passeword_input.clear()
passeword_input.send_keys(password)
button_next_xpath = '//input[@value="Se connecter"]'
click_on_connect = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, button_next_xpath))).click()

#%%


#%%



# from webdriver_manager.firefox import GeckoDriverManager
# url = 'https://airbnb.com/users/show/156996131'
# browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())#, options=option_browser)
# open_result(browser, url)  
# time.sleep(2) #the page charges
# close_cookies(browser)
# #save the main page handle
# main_page = browser.current_window_handle
# connect_with_google_XPATH = '//button[@aria-label="Continuer avec Google"]'
# connect_with_google = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, connect_with_google_XPATH))).click()
# # changing the handles to access login page
# for handle in browser.window_handles:
#     if handle != main_page:
#         login_page = handle
          
# # change the control to signin page        
# browser.switch_to.window(login_page)

# #enter mail
# mail = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='identifier']" )))
# mail.clear()
# mail.send_keys(email_adress)
# button_next_xpath = '//*[@id="identifierNext"]/div/button'
# click_on_next = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, button_next_xpath))).click()


#%%
# change control to main page
browser.switch_to.window(main_page)
l = ['https://airbnb.com/users/show/156996131', 'https://airbnb.com/users/show/171070956', 'https://airbnb.com/users/show/253639977', 'https://airbnb.com/users/show/231945489', 'https://airbnb.com/users/show/34210694', 'https://airbnb.com/users/show/184386847', 'https://airbnb.com/users/show/148484186', 'https://airbnb.com/users/show/48748063', 'https://airbnb.com/users/show/35069983', 'https://airbnb.com/users/show/27845401', 'https://airbnb.com/users/show/6037019', 'https://airbnb.com/users/show/328688439', 'https://airbnb.com/users/show/222169638', 'https://airbnb.com/users/show/125137938', 'https://airbnb.com/users/show/327123971', 'https://airbnb.com/users/show/167975811', 'https://airbnb.com/users/show/77339477', 'https://airbnb.com/users/show/89900203', 'https://airbnb.com/users/show/92688632', 'https://airbnb.com/users/show/53138922', 'https://airbnb.com/users/show/8617766', 'https://airbnb.com/users/show/95512877', 'https://airbnb.com/users/show/276590999', 'https://airbnb.com/users/show/309970794', 'https://airbnb.com/users/show/263899734', 'https://airbnb.com/users/show/222549438', 'https://airbnb.com/users/show/306454286', 'https://airbnb.com/users/show/253637232', 'https://airbnb.com/users/show/19418972', 'https://airbnb.com/users/show/306575312', 'https://airbnb.com/users/show/332016685', 'https://airbnb.com/users/show/316776424', 'https://airbnb.com/users/show/26033280', 'https://airbnb.com/users/show/71557490', 'https://airbnb.com/users/show/62346196', 'https://airbnb.com/users/show/147212632', 'https://airbnb.com/users/show/360131878', 'https://airbnb.com/users/show/189298885', 'https://airbnb.com/users/show/226476643', 'https://airbnb.com/users/show/264320786', 'https://airbnb.com/users/show/119092958', 'https://airbnb.com/users/show/64535307', 'https://airbnb.com/users/show/236740639', 'https://airbnb.com/users/show/315780648', 'https://airbnb.com/users/show/51132689', 'https://airbnb.com/users/show/344774275', 'https://airbnb.com/users/show/207000795', 'https://airbnb.com/users/show/209420266', 'https://airbnb.com/users/show/82501976', 'https://airbnb.com/users/show/295622799', 'https://airbnb.com/users/show/58233962', 'https://airbnb.com/users/show/27609483', 'https://airbnb.com/users/show/210161890', 'https://airbnb.com/users/show/17968911', 'https://airbnb.com/users/show/7112745', 'https://airbnb.com/users/show/4113224', 'https://airbnb.com/users/show/31743033', 'https://airbnb.com/users/show/169038014', 'https://airbnb.com/users/show/289777541', 'https://airbnb.com/users/show/4512372', 'https://airbnb.com/users/show/337273148', 'https://airbnb.com/users/show/264371521', 'https://airbnb.com/users/show/55764558', 'https://airbnb.com/users/show/335428879', 'https://airbnb.com/users/show/179450513', 'https://airbnb.com/users/show/196001459', 'https://airbnb.com/users/show/98380285', 'https://airbnb.com/users/show/26272287', 'https://airbnb.com/users/show/5248317', 'https://airbnb.com/users/show/248890582', 'https://airbnb.com/users/show/395139838', 'https://airbnb.com/users/show/45438083', 'https://airbnb.com/users/show/75048007', 'https://airbnb.com/users/show/296248822', 'https://airbnb.com/users/show/426929878', 'https://airbnb.com/users/show/369787671', 'https://airbnb.com/users/show/262360817', 'https://airbnb.com/users/show/404735623', 'https://airbnb.com/users/show/90313833', 'https://airbnb.com/users/show/189004526', 'https://airbnb.com/users/show/36875147', 'https://airbnb.com/users/show/142595984', 'https://airbnb.com/users/show/13402115', 'https://airbnb.com/users/show/5405265', 'https://airbnb.com/users/show/74008392', 'https://airbnb.com/users/show/142354337', 'https://airbnb.com/users/show/52163463', 'https://airbnb.com/users/show/62252074', 'https://airbnb.com/users/show/24767762', 'https://airbnb.com/users/show/32972720', 'https://airbnb.com/users/show/387162428', 'https://airbnb.com/users/show/347820960', 'https://airbnb.com/users/show/268973478', 'https://airbnb.com/users/show/26233795', 'https://airbnb.com/users/show/207250377', 'https://airbnb.com/users/show/368895655', 'https://airbnb.com/users/show/276651753', 'https://airbnb.com/users/show/34348969', 'https://airbnb.com/users/show/53973494', 'https://airbnb.com/users/show/12994445']
commentaires = []
countries = []
for url in l:
    #nb of comm
    open_result(browser, url) 
    nb_comm_xpath = '/html/body/div[5]/div/div/div[1]/div/div/div[1]/div[1]/main/div/div/div/div[1]/div/div[2]/button/div/span[2]'
    nb_com_web = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, nb_comm_xpath)))
    nb_com = nb_com_web.text
    commentaires.append(nb_com)
    #country
    location_xpath = '/html/body/div[5]/div/div/div[1]/div/div/div[1]/div[1]/main/div/div/div/div[2]/div/section/div[4]/section/div[3]/div/span[2]'
    location_web = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, nb_comm_xpath)))
    country = nb_com_web.text
    countries.append(nb_com)
    #time.sleep(1)

















