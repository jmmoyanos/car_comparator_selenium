from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
import re
import requests
from random import *
from tqdm import tqdm #progress bar
from datetime import datetime
import os
import glob
import pickle #for saving data
from src.utils import start_driver_selenium

def scrape_links_for_one_make_model(option, make_model_dat,sleep, save_to_csv):

    year_min = make_model_dat['year_min']
    year_max = make_model_dat['year_max']
    price_min = make_model_dat['price_min']
    price_max = make_model_dat['price_max']

    link = make_model_dat['link']
    str_filter = f"#/precio_from/{price_min}/precio_to/{price_max}/year_from/{year_min}/year_to/{year_max}"

    make_model_input_link = link + str_filter

    driver = start_driver_selenium(option)

    driver.get(make_model_input_link)
    time.sleep(sleep)
    driver.execute_script("window.scrollTo(0, 250)")
    for i in range(500,85000,750):
        driver.execute_script(f"window.scrollTo(0, {i})")
        time.sleep(0.05)

    make_model_link_lastpage_source = driver.page_source
    make_model_link_soup = BeautifulSoup(make_model_link_lastpage_source, 'html.parser')

    list_a = make_model_link_soup.find_all('a')
    lista_a_car = []
    for a in list_a:
        if ((make_model_dat['id2'] + '-' + make_model_dat['id1']) in str(a)) & ('jss' in str(a)):
            lista_a_car.append(a['class'][3])

    try:
        js = list(set(lista_a_car))[0]
    except:
        js=''
    a = make_model_link_soup.findAll('a', {'class': f'MuiTypography-root MuiLink-root MuiLink-underlineNone {js} MuiTypography-colorInherit'})

    links_on_page = ["https://www.flexicar.es" + link['href'] for link in a]

    links_on_one_page_df = pd.DataFrame({'ad_link' : links_on_page})
        #drop duplicates
    links_on_one_page_df = links_on_one_page_df.drop_duplicates()

    links_on_one_page_df['make_model_link'] = link #via this we can see which make and model the links belong to

    make_model_input_data = pd.DataFrame(make_model_dat).T

    #datetime string
    now = datetime.now() 
    datetime_string = str(now.strftime("%Y%m%d_%H%M%S"))

    links_on_one_page_df['download_date_time'] = datetime_string
    make_model_input_data = pd.DataFrame(make_model_dat).T

    if isinstance(make_model_input_data, pd.DataFrame):
            #join the dataframes to get make and model information
            links_on_one_page_df = pd.merge(links_on_one_page_df, make_model_input_data, how = 'left', left_on= ['make_model_link'], right_on = ['link'])
            
    if save_to_csv:
            #check if folder exists and if not create it
            if not os.path.exists('data/flexicar/make_model_ads_links'):
                os.makedirs('data/flexicar/make_model_ads_links')

            links_on_one_page_df.to_csv(str('./data/flexicar/make_model_ads_links/links_on_one_page_df' + datetime_string + '.csv'), index = False)

    driver.quit()
    return(links_on_one_page_df)

def multiple_link_on_multiple_pages_data(option, make_model_dat, sleep, save_to_csv):

    multiple_make_model_data = pd.DataFrame()
    lenght = make_model_dat.shape[0]
    for i in range(lenght):
        
        one_page_adds = scrape_links_for_one_make_model(option, make_model_dat.loc[i],
                                                        sleep = sleep, 
                                                        save_to_csv = save_to_csv)

        multiple_make_model_data = pd.concat([multiple_make_model_data, one_page_adds], ignore_index=True)
    
    return(multiple_make_model_data)

# concatenate the dataframes in one folder to get one file (with different columns)
def concatenate_dfs(indir, save_to_csv = True, save_to_pickle = True):
    

    fileList=glob.glob(str(str(indir) + "*.csv"))
    print("Found this many CSVs: ", len(fileList), " In this folder: ", str(os.getcwd()) + "/" + str(indir))

    output_file = pd.concat([pd.read_csv(filename) for filename in fileList])

    cols = list(set(output_file.columns) - set(['download_date_time']))
    output_file = output_file.drop_duplicates(subset=cols,keep='last')

    if save_to_csv:
        output_file.to_csv("data/flexicar/make_model_ads_links_concatinated.csv", index=False)

    if save_to_pickle:
        output_file.to_pickle("data/flexicar/make_model_ads_links_concatinated.pkl")

    return(output_file)


# if __name__ == "__main__":
def main(option):

    make_model_dat = pd.read_csv('./data/flexicar/make_and_model_links.csv')
        
    multi_data = multiple_link_on_multiple_pages_data(option,make_model_dat,
                                                      1, 
                                                      True)

    make_model_ads_data = concatenate_dfs(indir= "data/flexicar/make_model_ads_links/", save_to_csv = True, save_to_pickle = False)
