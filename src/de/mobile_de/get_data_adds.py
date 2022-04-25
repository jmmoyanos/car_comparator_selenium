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


def clean_data(data):
    data['price'] = data['Price'].str.replace(',', '')
    data['price'] = data['price'].str.extract('(\d+)').astype(int, errors='ignore')

    data = data[~data['price'].isna()]
    data['price'] = data['price'].astype(int)
    
    data['Mileage'] = data['Mileage'].str.replace('.', '')
    data['Mileage'] = data['Mileage'].str.extract('(\d+)').astype(int, errors='ignore')
    data = data[~data['Mileage'].isna()]
    data['Mileage'] = data['Mileage'].astype(int)
    
    # data['year'] = data['First Registration'].apply(lambda x : str(x).split('/')[1])
    # data['month'] = data['First Registration'].apply(lambda x : str(x).split('/')[0])
    data['price_category'] = data['Price'].str.extract('([a-zA-Z]+)')
    return data

def get_ad_data(option, ad_link = '', sleep_time = 5, save_to_csv = True, save_to_pickle = True):
    
    driver = start_driver_selenium(option)

    #get the number of pages
    driver.get(ad_link + '%3Flang%3Den&lang=en')
    time.sleep(sleep_time)
    ad_source = driver.page_source
    ad_soup = BeautifulSoup(ad_source, 'html.parser')
    driver.quit()

    try:
        table_pre = ad_soup.find("div", { "class" : "cBox-body cBox-body--technical-data"})
        all_div = table_pre.findAll("div", { "class" : re.compile('^g-col-6')})
    except:
        table_pre = []
        all_div = []
    
    description_list = []
    value_list = []

    try:
        div_length = len(all_div)
    except:
        div_length = 2

    i = 1
    for i in range(div_length - 1):
        try:
            description_list.append(all_div[i].text)
            value_list.append(all_div[i+1].text)
            i += 2
        except:
            description_list.append('no_description')
            value_list.append('no_value')

    #create a dataframe
    df = pd.DataFrame(list(zip(description_list, value_list)), columns = ['description', 'value'])

    #keep rows where value is equal to the followings
    data_we_want_to_keep = ['Price', 'Category', 'Mileage', 'Cubic Capacity', 'Power', 'Fuel', 'Number of Seats', 'Gearbox','Energy efficiency class', 'First Registration', 'Colour', 'Interior Design','Emissions Sticker','Parking sensors', 'Energy efficiency class']
    df = df[df['description'].isin(data_we_want_to_keep)]
    # df.columns = ['Price', 'Category', 'Mileage', 'Engine_Displacement', 'Power', 'Fuel_Type', 'Number of Seats', 'Transmission', 'First Registration', 'Color', 'Interior']

    # #transpose with description as column names
    #df = df.T
    df = df.set_index('description').T.reset_index(drop=True)
    df = df.rename_axis(None, axis=1)
    df['link'] = ad_link

    #datetime string
    now = datetime.now() 
    datetime_string = str(now.strftime("%Y%m%d_%H%M%S"))

    df['download_date_time'] = datetime_string

    #save the dataframe if save_to_csv is True
    if save_to_csv:
        #check if folder exists and if not create it
        if not os.path.exists('data/mobile_de/make_model_ads_data'):
            os.makedirs('data/mobile_de/make_model_ads_data')

        df.to_csv(str('data/mobile_de/make_model_ads_data/links_on_one_page_df' + datetime_string + '.csv'), index = False)

    if save_to_pickle:
        if not os.path.exists('data/mobile_de/make_model_ads_data'):
            os.makedirs('data/mobile_de/make_model_ads_data')
        
        df.to_pickle('data/mobile_de/make_model_ads_data/links_on_one_page_df' + datetime_string + "pkl")

    return(df)

# concatenate the dataframes in one folder to get one file (with different columns)
def concatenate_dfs(indir, save_to_csv = True, save_to_pickle = True):
    

    fileList=glob.glob(str(str(indir) + "*.csv"))
    print("Found this many CSVs: ", len(fileList), " In this folder: ", str(os.getcwd()) + "/" + str(indir))
    output_file = pd.concat([pd.read_csv(filename) for filename in fileList])
    cols = list(set(output_file.columns) - set(['download_date_time']))
    output_file = output_file.drop_duplicates(subset=cols,keep='last')

    if save_to_csv:
        output_file.to_csv("data/mobile_de/make_model_ads_concatinated.csv", index=False)

    if save_to_pickle:
        output_file.to_pickle("data/mobile_de/make_model_ads_concatinated.pkl")
    output_file.reset_index(drop=True, inplace=True)

    return(output_file)

# merge the individual ads data with the make_model_ads_data_latest and keep only the latest download date
def merge_make_model_keep_latest(data):
    latest_scrape = data.groupby(['link'], dropna=True).agg(number_of_ads=('link', 'count'), latest_scrape=('download_date_time', 'max'))
    latest_scrape = latest_scrape.reset_index()

    data = pd.merge(data, latest_scrape[['link', 'latest_scrape']], how = 'left', left_on = ['link'], right_on = ['link'])
    data = data.reset_index(drop=True)
    # keep rows where download_date_time is equal to latest_scrape
    data = data[data['download_date_time'] == data['latest_scrape']]
    data = data.reset_index(drop=True)
    # drop the latest_scrape column
    data = data.drop(columns = ['latest_scrape'])
    
    data = pd.merge(data, make_model_ads_data_latest[['ad_link', 'car_make', 'car_model']], how = 'left', left_on = 'link', right_on = 'ad_link')

    return data



# if __name__ == '__main__' :
def main(option):
    make_model_ads_data = pd.read_csv("./data/mobile_de/make_model_ads_links_concatinated.csv")

    latest_scrape = make_model_ads_data.groupby(['car_make', 'car_model'], dropna=False).agg(number_of_ads=('ad_link', 'count'), latest_scrape=('download_date_time', 'max'))
    latest_scrape = latest_scrape.reset_index()
    
    make_model_ads_data_latest = pd.merge(make_model_ads_data, latest_scrape[['car_make', 'car_model', 'latest_scrape']], how = 'left', left_on = ['car_make', 'car_model'], right_on = ['car_make', 'car_model'])
    make_model_ads_data_latest = make_model_ads_data_latest.reset_index(drop=True)
    # keep rows where download_date_time is equal to latest_scrape
    make_model_ads_data_latest = make_model_ads_data_latest[make_model_ads_data_latest['download_date_time'] == make_model_ads_data_latest['latest_scrape']]
    make_model_ads_data_latest = make_model_ads_data_latest.reset_index(drop=True)
    # drop the latest_scrape column
    make_model_ads_data_latest = make_model_ads_data_latest.drop(columns = ['latest_scrape'])

    len_of_links = len(make_model_ads_data_latest)

    for i in tqdm(range(len_of_links)):
        ad_link = make_model_ads_data_latest['ad_link'][i]
        data = get_ad_data(option, ad_link = ad_link, sleep_time = 5, save_to_csv = True, save_to_pickle = False)

    individual_ads_data = concatenate_dfs("./data/mobile_de/make_model_ads_data/",  True, False)

    ads_df = merge_make_model_keep_latest(data = individual_ads_data)
    ads_df_clean = clean_data(data = ads_df)


    if not os.path.exists('data/mobile_de/final_data'):
            os.makedirs('data/mobile_de/final_data')

    now = datetime.now() 
    datetime_string = str(now.strftime("%Y%m%d_%H%M%S"))
    ads_df_clean['audit_date'] = datetime_string
    ads_df_clean.to_csv(f'./data/mobile_de/final_data/scrap_mobilede_{datetime_string}.csv', index=False)