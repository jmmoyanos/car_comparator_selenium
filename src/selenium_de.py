from black import main
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup 
import pandas as pd
import numpy as np
import re
from random import randrange
from tqdm import tqdm #progress bar

chromedriver = "/usr/local/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

PROXY = "176.56.107.80"

def chromedriver_proxie(PROXY):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        wd = webdriver.Chrome(options=chrome_options)
        wd.implicitly_wait(2)
        return wd

def chromedriver_():
        wd = webdriver.Chrome()
        wd.implicitly_wait(1)
        return wd

def read_proxies(file):
        f = open(file, "r")
        proxies = f.read().split("\n")
        return proxies

def chromedriver_de():
        
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    return driver

if __name__ == "__main__":

        # wd = chromedriver_()

        url = "https://suchen.mobile.de/fahrzeuge/search.html?dam=0&ecol=BLACK&ecol=GREY&fr=2017%3A&isSearchRequest=true&ml=%3A125000&ms=3500%3B6%3B%3B%3B&od=up&p=10000%3A20000&ref=srp&refId=2804e431-ddff-3817-0f5f-0b62cf3f7222&s=Car&sb=p&sfmr=false&vc=Car?lang=en"
        url = "https://www.coches.net/segunda-mano/?MakeId=7&MaxKms=140000&MaxYear=2015&MinPrice=10000&MinYear=2015&ModelId=944"
        url = "https://www.flexicar.es/coches-segunda-mano/"
        proxies = read_proxies("./proxies.txt")
        
        wd = chromedriver_de()
        wd.get(url)
        time.sleep(3)
        html = wd.page_source
        soup = BeautifulSoup(html, "html.parser")

 
                
                