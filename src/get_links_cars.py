from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
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

def scrape_links_for_one_make_model(make_model_input_link , sleep, make_model_input_data, save_to_csv):

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2} # this is to not load images
    chrome_options.add_experimental_option("prefs", prefs)

    #start a driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

    #get the number of pages
    driver.get(make_model_input_link)
    make_model_link_lastpage_source = driver.page_source
    make_model_link_soup = BeautifulSoup(make_model_link_lastpage_source, 'html.parser')

    last_button = make_model_link_soup.findAll('span', {'class': 'btn btn--muted btn--s'})
    
    #if there is only one page, then this gives an error so we need to check for that
    try:
        print("This many pages found: ", last_button[len(last_button)-1].text)
        last_button_number = last_button[len(last_button)-1].text
        last_button_number = int(last_button_number)
    except:
        last_button_number = int(1)
    
    driver.close()

    #start scraping the ads
    
    links_on_multiple_pages = []

    for i in tqdm(range(1, last_button_number + 1)):

        #start a new driver every time
        #we need this to avoid getting blocked by the website. If we don't do this, we will get captcha

        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2} # this is to not load images
        chrome_options.add_experimental_option("prefs", prefs)

        #start a driver
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

        #we need to navigate to the page
        one_page_link = make_model_input_link + "&pageNumber=" + str(i)

        driver.get(one_page_link)
        time.sleep(sleep)
        base_source = driver.page_source
        base_soup = BeautifulSoup(base_source, 'html.parser')

        #get all the links
        cars_add_list_all = base_soup.findAll('a', {'class': re.compile('^link--muted no--text--decoration')})

        links_on_one_page = []

        for i in range(len(cars_add_list_all)):

            link = cars_add_list_all[i]['href']
            
            if not link.endswith('SellerAd'):
                # filter out links that end with 'SellerAd' (these are links to ads and we do not need them)
                links_on_one_page.append(link)

        for elements in links_on_one_page:
            links_on_multiple_pages.append(elements)

        driver.close() #close the driver

    links_on_one_page_df = pd.DataFrame({'ad_link' : links_on_multiple_pages})
    #drop duplicates
    links_on_one_page_df = links_on_one_page_df.drop_duplicates()

    links_on_one_page_df['make_model_link'] = make_model_input_link #via this we can see which make and model the links belong to
    
    #datetime string
    now = datetime.now() 
    datetime_string = str(now.strftime("%Y%m%d_%H%M%S"))

    links_on_one_page_df['download_date_time'] = datetime_string

    #check is the make and model is in the dataframe
    if isinstance(make_model_input_data, pd.DataFrame):
        #join the dataframes to get make and model information
        links_on_one_page_df = pd.merge(links_on_one_page_df, make_model_input_data, how = 'left', left_on= ['make_model_link'], right_on = ['link'])

    #save the dataframe if save_to_csv is True
    if save_to_csv:
        #check if folder exists and if not create it
        if not os.path.exists('data/de/make_model_ads_links'):
            os.makedirs('data/de/make_model_ads_links')

        links_on_one_page_df.to_csv(str('data/de/make_model_ads_links/links_on_one_page_df' + datetime_string + '.csv'), index = False)

    return(links_on_one_page_df)

def multiple_link_on_multiple_pages_data(make_model_input_links, sleep, make_model_input_data, save_to_csv):

    multiple_make_model_data = pd.DataFrame()

    for one_make_model_link in make_model_input_links:
        
        one_page_adds = scrape_links_for_one_make_model(make_model_input_link = one_make_model_link, sleep = sleep, make_model_input_data = make_model_input_data, save_to_csv = save_to_csv)
        multiple_make_model_data = pd.concat([multiple_make_model_data, one_page_adds], ignore_index=True)
    
    return(multiple_make_model_data)

# concatenate the dataframes in one folder to get one file (with different columns)
def concatenate_dfs(indir, save_to_csv = True, save_to_pickle = True):
    

    fileList=glob.glob(str(str(indir) + "*.csv"))
    print("Found this many CSVs: ", len(fileList), " In this folder: ", str(os.getcwd()) + "/" + str(indir))

    output_file = pd.concat([pd.read_csv(filename) for filename in fileList])
    print(output_file.shape)
    cols = list(set(output_file.columns) - set(['download_date_time']))
    output_file = output_file.drop_duplicates(subset=cols,keep='last')
    print(output_file.shape)

    if save_to_csv:
        output_file.to_csv("data/de/make_model_ads_links_concatinated.csv", index=False)

    if save_to_pickle:
        output_file.to_pickle("data/de/make_model_ads_links_concatinated.pkl")

    return(output_file)


if __name__ == "__main__":

    make_model_dat = pd.read_csv('./data/de/make_and_model_links.csv')
        
    multi_data = multiple_link_on_multiple_pages_data(make_model_dat['link'], 1, make_model_dat, True)

    make_model_ads_data = concatenate_dfs(indir= "data/de/make_model_ads_links/", save_to_csv = True, save_to_pickle = False)
