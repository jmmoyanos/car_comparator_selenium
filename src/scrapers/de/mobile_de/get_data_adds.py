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
from src.utils import start_driver_selenium, list_files, write_csv, read_csv,getBucket
import concurrent.futures



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

def get_ad_data(option, ad_link,make_model_link, sleep_time, save_to_csv,logger,bucket,storage_type):
    
    try:
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
        
        model = ad_soup.find("h1")    
        if model==None:
            model = ad_soup.find("h2")   
        if model==None:
            model = ad_soup.find("h3") 

        #create a dataframe
        df = pd.DataFrame(list(zip(description_list, value_list)), columns = ['description', 'value'])

        #keep rows where value is equal to the followings
        data_we_want_to_keep = ['Price', 'Category', 'Mileage', 'Cubic Capacity', 'Power', 'Fuel','Fuel Consumption ', 'Number of Seats', 'Gearbox','Energy efficiency class', 'First Registration', 'Colour', 'Interior Design','Emissions Sticker','Parking sensors', 'Energy efficiency class']
        df = df[df['description'].isin(data_we_want_to_keep)]
        # df.columns = ['Price', 'Category', 'Mileage', 'Engine_Displacement', 'Power', 'Fuel_Type', 'Number of Seats', 'Transmission', 'First Registration', 'Color', 'Interior']

        # #transpose with description as column names
        #df = df.T
        df = df.set_index('description').T.reset_index(drop=True)
        df = df.rename_axis(None, axis=1)
        df['link'] = ad_link
        df['make_model_link'] = make_model_link
        df['model'] = model


        #datetime string
        now = datetime.now() 
        datetime_string = str(now.strftime("%Y%m%d_%H%M%S%f"))

        df['download_date_time'] = datetime_string

        #save the dataframe if save_to_csv is True
        if save_to_csv:
            write_csv(storage_type,df,str('data/mobile_de/make_model_ads_data/links_on_one_page_df' + datetime_string + '.csv'),bucket)

        logger.info(f'-----> {name} - saving data from {ad_link}%3Flang%3Den&lang=en')
        del df 
    except Exception as exp:
        logger.error(f'-----> {name} - {exp} -saving data from {ad_link}%3Flang%3Den&lang=en')



# concatenate the dataframes in one folder to get one file (with different columns)
def concatenate_dfs(indir, save_to_csv,logger,bucket,storage_type):
    
    fileList = list_files(storage_type, indir, bucket)

    dfs = [read_csv(storage_type, path, bucket) for path in fileList]

    output_file = pd.concat(dfs)

    logger.info(f'-----> {name} - Found this many CSVs: {len(fileList)} In this folder: {str(indir)}')


    cols = list(set(output_file.columns) - set(['download_date_time']))
    output_file = output_file.drop_duplicates(subset=cols,keep='last')

    if save_to_csv:
        try:
            write_csv(storage_type,output_file,"data/mobile_de/make_model_ads_concatinated.csv",bucket)
            logger.info(f'-----> {name} - saving data/mobile_de/make_model_ads_concatinated.csv')
        except:
            logger.error(f'-----> {name} - saving data/mobile_de/make_model_ads_concatinated.csv')


    output_file.reset_index(drop=True, inplace=True)

    return(output_file)

# merge the individual ads data with the make_model_ads_data_latest and keep only the latest download date
def merge_make_model_keep_latest(data,make_model_ads_data_latest):
    latest_scrape = data.groupby(['link'], dropna=True).agg(number_of_ads=('link', 'count'), latest_scrape=('download_date_time', 'max'))
    latest_scrape = latest_scrape.reset_index()

    data = pd.merge(data, latest_scrape[['link', 'latest_scrape']], how = 'left', left_on = ['link'], right_on = ['link'])
    data = data.reset_index(drop=True)
    # keep rows where download_date_time is equal to latest_scrape
    data = data[data['download_date_time'] == data['latest_scrape']]
    data = data.reset_index(drop=True)
    # drop the latest_scrape column
    data = data.drop(columns = ['latest_scrape'])
    make_model_ads_data_latest = make_model_ads_data_latest[['make_model_link','car_make', 'car_model']].drop_duplicates(keep='first')

    data = pd.merge(data, make_model_ads_data_latest, how = 'inner', left_on = 'make_model_link', right_on = 'make_model_link')

    return data



# if __name__ == '__main__' :
def main(option,num_workers,logger, storage_type):

    global name
    name='mobile_de'
    bucket = getBucket(storage_type)

    
    logger.info(f'-----> {name} - reading make_model_ads_links_concatinated')
    make_model_ads_data = read_csv(storage_type,"data/mobile_de/make_model_ads_links_concatinated.csv", bucket)

    latest_scrape = make_model_ads_data.groupby(['car_make', 'car_model'], dropna=False).agg(number_of_ads=('ad_link', 'count'), latest_scrape=('download_date_time', 'max'))
    latest_scrape = latest_scrape.reset_index()
    
    make_model_ads_data_latest = pd.merge(make_model_ads_data, latest_scrape[['car_make', 'car_model', 'latest_scrape']], how = 'left', left_on = ['car_make', 'car_model'], right_on = ['car_make', 'car_model'])
    make_model_ads_data_latest = make_model_ads_data_latest.reset_index(drop=True)
    # keep rows where download_date_time is equal to latest_scrape
    make_model_ads_data_latest = make_model_ads_data_latest[make_model_ads_data_latest['download_date_time'] == make_model_ads_data_latest['latest_scrape']]
    make_model_ads_data_latest = make_model_ads_data_latest.reset_index(drop=True)
    # drop the latest_scrape column
    make_model_ads_data_latest = make_model_ads_data_latest.drop(columns = ['latest_scrape'])
    logger.info(f'-----> {name} - getting ad data of the last scrap')


    len_of_links = len(make_model_ads_data_latest)
    ad_links  = make_model_ads_data_latest['ad_link'].tolist()
    make_model_link  = make_model_ads_data_latest['make_model_link'].tolist()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(get_ad_data, option, ad_links[i],make_model_link[i], 5,True,logger,bucket,storage_type): i for i in range(len_of_links)}
        for future in tqdm(concurrent.futures.as_completed(future_to_url),"Progress: "):
            url = future_to_url[future]
            try:
                logger.info(f'-----> {name} -  {url}/{len_of_links} getting ad data - {ad_links[url]}')
            except:
                logger.error(f'-----> {name} - getting ad data - {ad_links[url]}')
    
    logger.info(f'-----> {name} - contatenate all df links scraped before')
    individual_ads_data = concatenate_dfs("data/mobile_de/make_model_ads_data/",  True,logger,bucket,storage_type)

    logger.info(f'-----> {name} - Merging data')
    ads_df = merge_make_model_keep_latest(data = individual_ads_data, make_model_ads_data_latest = make_model_ads_data_latest)
    ads_df_clean = clean_data(data = ads_df)

    try:
        now = datetime.now() 
        datetime_string = str(now.strftime("%Y%m%d_%H%M%S"))
        ads_df_clean['audit_date'] = datetime_string
        write_csv(storage_type,ads_df_clean,f'data/mobile_de/final_data/scrap_mobilede_{datetime_string}.csv',bucket)
        logger.info(f'-----> {name} - Saving merged data onto /data/mobile_de/final_data/scrap_mobilede_{datetime_string}.csv')
    except:
        logger.error(f'-----> {name} - Saving merged data onto /data/mobile_de/final_data/scrap_mobilede_{datetime_string}.csv')
