# from black import main
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
import re
from random import randrange
from tqdm import tqdm #progress bar
from src.utils import start_driver_selenium , get_notion_database, read_csv, write_csv, getBucket
import os
import pandas as pd
from src.storage import GStorage

def get_all_make_model(option,mobile_de_eng_base_link, save_filename, df_cars,bucket,storage_type,logger):

    logger.info(f'-----> {name}  - getting the master makes links')
    list_cars = df_cars['Name'].unique().tolist()
    list_cars_makes = [car.split(' ')[0] for car in list_cars]
    
    driver = start_driver_selenium(option)

    driver.get(mobile_de_eng_base_link)
    time.sleep(3)
    base_source = driver.page_source
    base_soup = BeautifulSoup(base_source, 'html.parser')

    make_list = base_soup.findAll('div', {'class': 'form-group'})[0]
    one_make = make_list.findAll('option')

    car_make = []
    id1 = []

    for i in range(len(one_make)):

        car_make.append(one_make[i].text.strip())

        try:
            id1.append(one_make[i]['value'])
        except:
            id1.append('')

    car_base_make_data = pd.DataFrame({'car_make': car_make, 'id1': id1})

    car_make_filter_out = ['Any', 'Other', '']
    car_base_make_data = car_base_make_data[~car_base_make_data.car_make.isin(car_make_filter_out)]
    car_base_make_data = car_base_make_data.drop_duplicates()
    car_base_make_data = car_base_make_data.reset_index(drop=True)
    car_base_make_data = car_base_make_data[car_base_make_data['car_make'].isin(list_cars_makes)]

    car_base_model_data = pd.DataFrame()

    for one_make in tqdm(car_base_make_data['car_make'], "Progress: "):

        try:
            make_string = "//select[@name='mk']/option[text()='{}']".format(one_make)
            driver.find_element(by=By.XPATH, value=make_string).click()
            time.sleep(3)

            base_source = driver.page_source
            base_soup = BeautifulSoup(base_source, 'html.parser')

            model_list = base_soup.findAll('div', {'class': 'form-group'})[1]
            models = model_list.findAll('option')

            car_model = []
            id2 = []

            for i in range(len(models)):

                car_model.append(models[i].text.strip())

                try:
                    id2.append(models[i]['value'])
                except:
                    id2.append('')

            car_base_model_data_aux = pd.DataFrame({'car_model': car_model, 'id2': id2})
            car_base_model_data_aux['car_make'] = one_make

            car_base_model_data = pd.concat([car_base_model_data, car_base_model_data_aux], ignore_index=True)
            logger.info(f'-----> {name}  - getting the master makes links {one_make}')

        except:
            logger.info(f'-----> {name}  - error getting the master makes links {one_make}')


    ###MAKE THE FILTERING HEREEEE
    
    if len(list_cars) > 0:
        lista_dfs = []

        for car in list_cars:
            brand = car.split(" ")[0]
            model = car.split(" ")[1]
            lista_dfs.append(car_base_model_data[(car_base_model_data["car_make"] == brand) & 
                            (car_base_model_data["car_model"] == model)])

        car_base_model_data = pd.concat(lista_dfs)


    car_data_base = pd.merge(car_base_make_data, car_base_model_data, left_on=['car_make'], right_on=['car_make'], how='right')
    car_data_base = car_data_base[~car_data_base.id2.isin([""])]
    # car_data_base = car_data_base[car_data_base.id2.apply(lambda x: x.isnumeric())]
    car_data_base = car_data_base.drop_duplicates()

    #####
    
    car_data_base['link'] = "https://suchen.mobile.de/fahrzeuge/search.html?dam=0&isSearchRequest=true&ms=" + car_data_base['id1'] + ";" + car_data_base['id2'] +  "&ref=quickSearch&sfmr=false&vc=Car"
    car_data_base = car_data_base.reset_index(drop=True)
    car_data_base['Name'] = car_data_base['car_make'] + ' ' +car_data_base['car_model']
    car_data_base = car_data_base.merge(df_cars, on='Name', how='inner')

    if len(save_filename) > 0:
        write_csv(storage_type,car_data_base,save_filename,bucket)
        logger.info(f'-----> {name}  - saving {save_filename}')

    
    try:
        driver.quit()
    except:
        print("driver closed")


    return(car_data_base)



#if __name__ == "__main__":
def main(option,logger,storage_type):

    try:

        df = get_notion_database('mobile_de').astype(str).sort_values(by='Name').reset_index(drop=True)

        global name
        name = 'mobile_de'

        bucket = getBucket(storage_type)

        try:
            df_cars_check = read_csv(storage_type,'data/mobile_de/make_and_model_links.csv',bucket)
            df_cars_check = df_cars_check[list(df.columns)].astype(str).sort_values(by='Name').reset_index(drop=True)

        except:
            df_cars_check = pd.DataFrame()
            logger.info(f'-----> {name} master not found')

        if not df.equals(df_cars_check):
            get_all_make_model( option,
                                "https://www.mobile.de/?lang=en", 
                                "data/mobile_de/make_and_model_links.csv",
                                df,
                                bucket,
                                storage_type,
                                logger)
        logger.info(f'-----> {name}  - master ended correctly')

    except Exception as e:
        logger.error(f'-----> {name}  - master ended correctly {e}')
