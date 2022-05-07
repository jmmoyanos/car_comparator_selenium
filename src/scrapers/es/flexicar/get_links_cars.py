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
from src.utils import start_driver_selenium, list_files, write_csv, read_csv,getBucket
import concurrent.futures

def scrape_links_for_one_make_model(option, make_model_dat,sleep, save_to_csv,bucket,storage_type,logger):

    year_min = make_model_dat['year_min']
    year_max = make_model_dat['year_max']
    price_min = make_model_dat['price_min']
    price_max = make_model_dat['price_max']

    link = make_model_dat['link']
    str_filter = f"#/precio_from/{price_min}/precio_to/{price_max}/year_from/{year_min}/year_to/{year_max}"

    make_model_input_link = link + str_filter

    driver = start_driver_selenium(option)

    driver.get(make_model_input_link)
    
    driver.execute_script("window.scrollTo(0, 250)")
    for i in range(500,85000,750):
        driver.execute_script(f"window.scrollTo(0, {i})")
        time.sleep(0.05)
    time.sleep(sleep)
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
    datetime_string = str(now.strftime("%Y%m%d_%H%M%S%f"))

    links_on_one_page_df['download_date_time'] = datetime_string
    make_model_input_data = pd.DataFrame(make_model_dat).T

    if isinstance(make_model_input_data, pd.DataFrame):
            #join the dataframes to get make and model information
            links_on_one_page_df = pd.merge(links_on_one_page_df, make_model_input_data, how = 'left', left_on= ['make_model_link'], right_on = ['link'])
            
    if save_to_csv:
        write_csv(storage_type, links_on_one_page_df,str(f'data/{name}/make_model_ads_links/links_on_one_page_df' + datetime_string + '.csv'),bucket)

    driver.quit()
    return(links_on_one_page_df)

def multiple_link_on_multiple_pages_data(option, num_workers,make_model_dat, sleep, save_to_csv,bucket,storage_type,logger):

    multiple_make_model_data = []
    len_of_links = make_model_dat.shape[0]

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(scrape_links_for_one_make_model, option, make_model_dat.loc[i], sleep,save_to_csv,bucket,storage_type,logger): i for i in range(len_of_links)}
        for future in tqdm(concurrent.futures.as_completed(future_to_url),"Progress: "):
            url = future_to_url[future]
            link = make_model_dat.loc[url]['link']
            try:
                one_page_adds = future.result()
                multiple_make_model_data.append(one_page_adds)
                logger.info(f'-----> {name} - scraping link page {url}  - {link}')

            except Exception as exc:
              logger.error(f'-----> {name} - scraping link page {url}  - {link}')

               #continue
            
    multiple_make_model_data = pd.concat(multiple_make_model_data)
    
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
        logger.info(f'-----> {name} - saving concate df links')
        # output_file.to_csv("data/mobile_de/make_model_ads_links_concatinated.csv", index=False)
        write_csv(storage_type,output_file,f"data/{name}/make_model_ads_links_concatinated.csv",bucket)

    return(output_file)

# if __name__ == "__main__":
def main(option,num_workers, logger, storage_type):

    try: 
        global name
        name='flexicar'
        
        logger.info(f'-----> {name} - reading make_and_model_links')
        
        bucket = getBucket(storage_type)

        make_model_dat = read_csv(storage_type,f'data/{name}/make_and_model_links.csv', bucket)
        
        logger.info(f'-----> {name} - calling multiple_link_on_multiple_pages_data')  
        multiple_link_on_multiple_pages_data(option,num_workers,make_model_dat,
                                                        1, 
                                                        True,bucket,storage_type,logger)

        logger.info(f'-----> {name} - calling concatenate_dfs')  
        concatenate_dfs(indir= f"data/{name}/make_model_ads_links/", save_to_csv = True , bucket=bucket,logger=logger, storage_type=storage_type)
        logger.info(f'-----> {name}  - links ended correctly')

    except Exception as e:

        logger.error(f'-----> {name}  - links ended with error {e}')
    