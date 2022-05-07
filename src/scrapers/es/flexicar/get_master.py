from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
from random import randrange
from tqdm import tqdm #progress bar
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from src.utils import start_driver_selenium , get_notion_database, read_csv, write_csv, getBucket
import concurrent.futures


def click_wait(driver,make):
    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, make))).click()

def get_car_model_page(i,option,num_workers,flexicar_base_link):

    brand_string_button = '//*[@id="brand-select"]'
    model_string_button = '//*[@id="model-select"]'
    make_out_page_brands = '//*[@id="menu-brands"]'

    k = 0
    while(k<5):
        try:
            list_ = []
            driver = start_driver_selenium(option)
            driver.get(flexicar_base_link)
            time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, 250)")
            time.sleep(1.5)
            driver.find_element(by=By.XPATH, value=brand_string_button).click()
            make_string = f'//*[@id="menu-brands"]/div[3]/ul/li[{i}]'
            time.sleep(0.3)
            try:
                make = driver.find_element(by=By.XPATH, value=make_string).text
            except:
                make=''
                
            time.sleep(0.3)
            click_wait(driver,make_string)
            time.sleep(0.3)
            click_wait(driver,make_out_page_brands)
            time.sleep(0.3)
            click_wait(driver,model_string_button)
            time.sleep(0.3)
            #print(make)
            try:
                model_make_string = '//*[@id="menu-models"]/div[3]/ul/li'
                time.sleep(0.1)
                list_.append(driver.find_element(by=By.XPATH, value=model_make_string).text)
                raise ValueError('A very specific bad thing happened.')

            except:
                try:
                    j=2
                    while(True):
                        model_make_string = f'//*[@id="menu-models"]/div[3]/ul/li[{j}]'
                        list_.append(driver.find_element(by=By.XPATH, value=model_make_string).text)
                        j+=1
                except:
                        time.sleep(0.5)
        except:
            driver.quit()
        
        k+=1
        if make!='' and list_!='':
            break

    try:
        driver.quit()
    except:
        print(i,k,"closed")

    return make,list_

def get_all_make_model(option, num_workers,flexicar_base_link, save_filename, df_cars, bucket,storage_type,logger):

    lista_makes = []
    lista_models = []

    logger.info(f'-----> {name}  - getting the master makes links')


    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
    # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(get_car_model_page,i,option,num_workers,flexicar_base_link): i for i in range(45)}
        for future in tqdm(concurrent.futures.as_completed(future_to_url),"Progress: "):
                try:
                    car_make, lista_models_id = future.result()
                    if (car_make!= '' and lista_models_id != []):
                        lista_makes.append(car_make)
                        lista_models.append(lista_models_id)
                        logger.info(f'-----> {name}  - getting the master makes links {car_make}')
                except:
                    logger.error(f'-----> {name}  - getting the master makes links {car_make}')


    car_base_make_data = pd.DataFrame(
    {'car_make': lista_makes,
     'id1': lista_models,
    })
    
    # explode and set ids and transform car_model and car_make columns
    car_base_make_data = car_base_make_data.explode('id1').reset_index(drop=True)
    car_base_make_data = car_base_make_data.replace(' ', '-', regex=True)
    car_base_make_data['car_model'] = car_base_make_data['id1']
    car_base_make_data['id2'] = car_base_make_data['car_make']
    car_base_make_data['id2'] = car_base_make_data['id2'].str.lower()
    car_base_make_data['id1'] = car_base_make_data['id1'].str.lower()
    car_data_base = car_base_make_data.drop_duplicates()

    #transform de problem of clase -> class
    
    car_data_base_class = car_data_base.loc[car_data_base['car_model'].str.contains('Clase', regex=True)]
    car_data_base_class['car_model']= car_data_base_class['car_model'].apply(lambda x: x.split('-')) \
                                                        .apply(lambda x: x[-1]+'-'+x[0] if len(x)>1 else x[0]) \
                                                        .replace('Clase', 'Class', regex=True)
    car_data_base = car_data_base.loc[~car_data_base['car_model'].str.contains('Clase', regex=True)]

    car_data_base = pd.concat([car_data_base,car_data_base_class])

    #car_data.reset_index(drop=True, inplace=True)
    car_data_base['link'] = flexicar_base_link + car_data_base['id2'] +  "/" + car_data_base['id1'] + "/segunda-mano/"
    car_data_base = car_data_base.reset_index(drop=True)
    car_data_base['Name'] = car_data_base['car_make'] + ' ' +car_data_base['car_model']

    car_data_base = car_data_base.merge(df_cars, on='Name', how='inner')


    if len(save_filename) > 0:
        try:
            write_csv(storage_type,car_data_base,save_filename,bucket)
            logger.info(f'-----> {name}  - saving {save_filename}')
        except:
            logger.error(f'-----> {name}  - saving {save_filename}')




    return(car_data_base)



# if __name__ == "__main__":
def main(option,num_workers, logger, storage_type):
    
    try:

        df = get_notion_database('flexicar').astype(str).sort_values(by='Name').reset_index(drop=True)

        global name
        name = 'flexicar'

        bucket = getBucket(storage_type)

        try:
            df_cars_check = read_csv(storage_type,'data/flexicar/make_and_model_links.csv',bucket)
            df_cars_check = df_cars_check[list(df.columns)].astype(str).sort_values(by='Name').reset_index(drop=True)
            

        except:
            df_cars_check = pd.DataFrame()
            logger.info(f'-----> {name} master not found')



        
        if not df.equals(df_cars_check):
            print("entro")
            get_all_make_model( option,num_workers,
                                "https://www.flexicar.es/", 
                                "data/flexicar/make_and_model_links.csv",
                                df,
                                bucket,
                                storage_type,
                                logger)
        logger.info(f'-----> {name}  - master ended correctly')
    
    except Exception as e:

        logger.error(f'-----> {name}  - master ended {e}')


