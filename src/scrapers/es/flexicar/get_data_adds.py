from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
from random import *
from tqdm import tqdm #progress bar
from datetime import datetime
import os
import glob
import pickle #for saving data
from src.utils import start_driver_selenium, list_files, write_csv, read_csv,getBucket
import concurrent.futures

def clean_data(data):
    data['price'] = data['Price'].str.replace('.', '')
    data['price'] = data['price'].str.extract('(\d+)').astype(int, errors='ignore')

    data = data[~data['price'].isna()]
    data['price'] = data['price'].astype(int)
    
    # data['year'] = data['First Registration'].apply(lambda x : str(x).split('/')[1])
    # data['month'] = data['First Registration'].apply(lambda x : str(x).split('/')[0])
    data['price_category'] = data['Price'].str.extract('([a-zA-Z]+)')
    return data

def get_ad_data(option, ad_link, sleep_time ,save_to_csv,logger,bucket,storage_type):
    driver = start_driver_selenium(option)

    #get the number of pages
    driver.get(ad_link)

    #scroll
    driver.execute_script(f"window.scrollTo(0, 1000)")

    time.sleep(sleep_time)
    ad_source = driver.page_source
    ad_soup = BeautifulSoup(ad_source, 'html.parser')
    driver.quit()

    list_data_ad = [data.text for data in ad_soup.find_all('strong') if 'js' in str(data)]
    list_ad_price = [data.text for data in ad_soup.find_all('h3') if '€' in str(data)]
    p = [data.text for data in ad_soup.find_all('p', class_="MuiTypography-root MuiTypography-body1")][:2]

    energy_sticker = ['']    
    for i in ad_soup.find_all('li'):
        if 'Etiqueta de eficiciencia energética clase' in i.text:
            energy_sticker = (i.text.split(' ')[-1:])
    interior = ['']     
    for i in ad_soup.find_all('li'):
        if 'Asientos de' in i.text:
            interior = [i.text]
   
    list_all_data_ad = list_data_ad + list_ad_price + p + energy_sticker + interior

    data_we_want_to_keep = ['First Registration','Mileage', 'Fuel','Number of Seats','Cubic Capacity','Colour','Gearbox', 'Consume', 'IVA', 'Price', 'model_type', 'location', 'Emissions Sticker', 'Interior']

    df = pd.DataFrame(list_all_data_ad).T
    df.columns = data_we_want_to_keep

    df = clean_data(df)

    df['link'] = ad_link

    #datetime string
    now = datetime.now() 
    datetime_string = str(now.strftime("%Y%m%d_%H%M%S5%f"))

    df['download_date_time'] = datetime_string

    #save the dataframe if save_to_csv is True
     #save the dataframe if save_to_csv is True
    if save_to_csv:
        write_csv(storage_type,df,str(f'data/{name}/make_model_ads_data/links_on_one_page_df' + datetime_string + '.csv'),bucket)
    return df

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
            write_csv(storage_type,output_file,f"data/{name}/make_model_ads_concatinated.csv",bucket)
            logger.info(f'-----> {name} - saving data/{name}/make_model_ads_concatinated.csv')
        except:
            logger.error(f'-----> {name} - saving data/{name}/make_model_ads_concatinated.csv')


    output_file.reset_index(drop=True, inplace=True)

    return(output_file)
# merge the individual ads data with the make_model_ads_data_latest and keep only the latest download date
def merge_make_model_keep_latest(data, make_model_ads_data):
    latest_scrape = data.groupby(['link'], dropna=True).agg(number_of_ads=('link', 'count'), latest_scrape=('download_date_time', 'max'))
    latest_scrape = latest_scrape.reset_index()

    data = pd.merge(data, latest_scrape[['link', 'latest_scrape']], how = 'left', left_on = ['link'], right_on = ['link'])
    data = data.reset_index(drop=True)
    # keep rows where download_date_time is equal to latest_scrape
    data = data[data['download_date_time'] == data['latest_scrape']]
    data = data.reset_index(drop=True)
    # drop the latest_scrape column
    data = data.drop(columns = ['latest_scrape'])
    
    data = pd.merge(data, make_model_ads_data[['ad_link', 'car_make', 'car_model']], how = 'left', left_on = 'link', right_on = 'ad_link')

    return data



# if __name__ == '__main__' :
def main(option,num_workers,logger, storage_type):

    global name
    name='flexicar'
    bucket = getBucket(storage_type)

    
    logger.info(f'-----> {name} - reading make_model_ads_links_concatinated')
    make_model_ads_data = read_csv(storage_type,f"data/{name}/make_model_ads_links_concatinated.csv", bucket)
    
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
        future_to_url = {executor.submit(get_ad_data, option, make_model_ads_data_latest['ad_link'][i], 5,True,logger,bucket,storage_type): i for i in range(len_of_links)}
        for future in tqdm(concurrent.futures.as_completed(future_to_url),"Progress: "):
            url = future_to_url[future]
            try:
                logger.info(f'-----> {name} - getting ad data - {ad_links[url]}')
            except:
                logger.error(f'-----> {name} - getting ad data - {ad_links[url]}')
    
    logger.info(f'-----> {name} - contatenate all df links scraped before')
    individual_ads_data = concatenate_dfs(f"data/{name}/make_model_ads_data/",  True,logger,bucket,storage_type)

    print(make_model_ads_data_latest)
    logger.info(f'-----> {name} - Merging data')
    ads_df = merge_make_model_keep_latest(individual_ads_data,make_model_ads_data_latest)
    ads_df_clean = clean_data(data = ads_df)

    try:
        now = datetime.now() 
        datetime_string = str(now.strftime("%Y%m%d_%H%M%S"))
        ads_df_clean['audit_date'] = datetime_string
        write_csv(storage_type,ads_df_clean,f'data/{name}/final_data/scrap_{name}_{datetime_string}.csv',bucket)
        logger.info(f'-----> {name} - Saving merged data onto /data/{name}/final_data/scrap_mobilede_{datetime_string}.csv')
    except:
        logger.error(f'-----> {name} - Saving merged data onto /data/{name}/final_data/scrap_mobilede_{datetime_string}.csv')