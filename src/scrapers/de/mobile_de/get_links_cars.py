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
import pickle #for saving data
from src.utils import start_driver_selenium, list_files, write_csv, read_csv,getBucket
import concurrent.futures
from src.storage import GStorage
import glob



def get_links_page(option,sleep,make_model_input_link,i):

        #start a new driver every time
        #we need this to avoid getting blocked by the website. If we don't do this, we will get captcha

        driver = start_driver_selenium(option)

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
        links_on_multiple_pages = []

        for elements in links_on_one_page:
            links_on_multiple_pages.append(elements)

        driver.quit() #quit the driver

        return links_on_multiple_pages

def scrape_links_for_one_make_model(option,num_workers,make_model_dat,sleep, save_to_csv,bucket,storage_type,logger):

    driver = start_driver_selenium(option)

    year_min = make_model_dat['year_min']
    year_max = make_model_dat['year_max']
    km_max = make_model_dat['km_max']
    price_min = make_model_dat['price_min']
    price_max = make_model_dat['price_max']
    name_model = make_model_dat['car_make'] + ' ' + make_model_dat['car_model']


    str_1 = make_model_dat['link'][:73]
    str_2 = make_model_dat['link'][73:]
    str_3 = f"&fr={year_min}%3A{year_max}&ml=%3A{km_max}&ms={make_model_dat['id1']}%3B6%3B%3B%3B&p={price_min}%3A{price_max}"

    make_model_input_link = str_1 + str_3 + str_2

    #get the number of pages
    driver.get(make_model_input_link)
    make_model_link_lastpage_source = driver.page_source
    make_model_link_soup = BeautifulSoup(make_model_link_lastpage_source, 'html.parser')

    last_button = make_model_link_soup.findAll('span', {'class': 'btn btn--secondary btn--l'})
    
    #if there is only one page, then this gives an error so we need to check for that
    try:
        print("This many pages found: ", last_button[len(last_button)-1].text)
        last_button_number = last_button[len(last_button)-1].text
        last_button_number = int(last_button_number)
    except:
        last_button_number = int(1)

    driver.quit()

    #start scraping the ads
    logger.info(f'-----> {name} - number of buttons pages - {name_model} - {last_button_number}')
    
    links_on_multiple_pages = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(get_links_page, option,sleep,make_model_input_link,i): i for i in range(last_button_number)}
        
        for future in tqdm(concurrent.futures.as_completed(future_to_url),"Progress: "):
            url = future_to_url[future]
            try:
                data = future.result()
                links_on_multiple_pages.append(data)
                logger.info(f'-----> {name} - number of buttons pages - {name_model} - {url}/{last_button_number} - {make_model_input_link + "&pageNumber=" + str(url)} ')
            except Exception as exc:
                logger.error(f'-----> {name} - number of buttons pages - {name_model} - {url}/{last_button_number} - {exc}')
               

    flat_list = [item for sublist in links_on_multiple_pages for item in sublist]
    links_on_one_page_df = pd.DataFrame({'ad_link' : flat_list})
    #drop duplicates
    links_on_one_page_df = links_on_one_page_df.drop_duplicates()

    links_on_one_page_df['make_model_link'] = make_model_input_link #via this we can see which make and model the links belong to
    
    #datetime string
    now = datetime.now() 
    datetime_string = str(now.strftime("%Y%m%d_%H%M%S%f"))

    links_on_one_page_df['download_date_time'] = datetime_string
    make_model_input_data = pd.DataFrame(make_model_dat).T
    make_model_input_data  = pd.concat(links_on_one_page_df.shape[0] * [make_model_input_data]).reset_index(drop=True)
    #check is the make and model is in the dataframe
    if isinstance(make_model_input_data, pd.DataFrame):
        #join the dataframes to get make and model information
        links_on_one_page_df = pd.concat([links_on_one_page_df, make_model_input_data],axis=1)

    #save the dataframe if save_to_csv is True
    if save_to_csv:
        write_csv(storage_type, links_on_one_page_df,str('data/mobile_de/make_model_ads_links/links_on_one_page_df' + datetime_string + '.csv'),bucket)

    return(links_on_one_page_df)

def multiple_link_on_multiple_pages_data(option,num_workers,make_model_dat, sleep, save_to_csv,bucket,storage_type,logger):

    multiple_make_model_data = pd.DataFrame()
    lenght = make_model_dat.shape[0]
    for i in tqdm(range(lenght),"Progress: "):
        link = make_model_dat.loc[i]['link']
        name_model = make_model_dat.loc[i]['car_make'] + ' ' +make_model_dat.loc[i]['car_model']
        try:
            logger.info(f'-----> {name} - scraping link {i}  - {name_model} -{link}')
            one_page_adds = scrape_links_for_one_make_model(option,num_workers, make_model_dat.loc[i],
                                                           sleep,save_to_csv,bucket,storage_type,logger)
            multiple_make_model_data = pd.concat([multiple_make_model_data, one_page_adds], ignore_index=True)
        except:
            logger.error(f'-----> {name} - scraping link {i}  - {name_model} -{link}')

    
    return(multiple_make_model_data)

# concatenate the dataframes in one folder to get one file (with different columns)
def concatenate_dfs(indir, save_to_csv,bucket,logger,storage_type):
    

    # fileList=glob.glob(str(str(indir) + "*.csv"))

    fileList = list_files(storage_type, indir, bucket)

    dfs = [read_csv(storage_type, path, bucket) for path in fileList]

    output_file = pd.concat(dfs)

    logger.info(f'-----> {name} - Found this many CSVs: {len(fileList)} In this folder: {str(indir)}')
   
    cols = list(set(output_file.columns) - set(['download_date_time']))
    output_file = output_file.drop_duplicates(subset=cols,keep='last')

    if save_to_csv:
        logger.error(f'-----> {name} - saving concate df links')
        # output_file.to_csv("data/mobile_de/make_model_ads_links_concatinated.csv", index=False)
        write_csv(storage_type,output_file,"data/mobile_de/make_model_ads_links_concatinated.csv",bucket)

    return(output_file)


def main(option,num_workers,logger, storage_type):

    try: 
        global name
        name='mobile_de'
        
        logger.info(f'-----> {name} - reading make_and_model_links')
        
        bucket = getBucket(storage_type)

        make_model_dat = read_csv(storage_type, 'data/mobile_de/make_and_model_links.csv', bucket)
        
        logger.info(f'-----> {name} - calling multiple_link_on_multiple_pages_data')  
        multiple_link_on_multiple_pages_data(option,num_workers,make_model_dat,
                                                        1, 
                                                        True,bucket,storage_type,logger)

        logger.info(f'-----> {name} - calling concatenate_dfs')  
        concatenate_dfs(indir= "data/mobile_de/make_model_ads_links/", save_to_csv = True , bucket=bucket,logger=logger, storage_type=storage_type)
        logger.info(f'-----> {name}  - links ended correctly')

    except Exception as e:

        logger.error(f'-----> {name}  - links ended with error {e}')
