import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time 
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

chromedriver = "/usr/local/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver

PROXY = "176.56.107.80"

def chromedriver_proxie(PROXY):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)
        wd = webdriver.Chrome(chrome_options=chrome_options)
        wd.implicitly_wait(1)
        return wd

def chromedriver():
        wd = webdriver.Chrome()
        wd.implicitly_wait(1)
        return wd

def read_proxies(file):
        f = open(file, "r")
        proxies = f.read().split("\n")
        return proxies

if __name__ == "__main__":

        # wd = chromedriver()

        url = "https://suchen.mobile.de/fahrzeuge/search.html?dam=0&ecol=BLACK&ecol=GREY&fr=2017%3A&isSearchRequest=true&ml=%3A125000&ms=3500%3B6%3B%3B%3B&od=up&p=10000%3A20000&ref=srp&refId=2804e431-ddff-3817-0f5f-0b62cf3f7222&s=Car&sb=p&sfmr=false&vc=Car?lang=en"
        url = "https://www.coches.net/segunda-mano/?MakeId=7&MaxKms=140000&MaxYear=2015&MinPrice=10000&MinYear=2015&ModelId=944"
        proxies = read_proxies("proxies.txt")
        for proxie in proxies:
                wd = chromedriver_proxie(proxie)
                wd.get(url)

                html = wd.page_source
                soup = BeautifulSoup(html, "html.parser")
                
                if 'mobile.de' in url:
                        bloques = soup.select('hitcounters')

                        for link in soup.find_all('script'):
                                if 'config' in link.get_text()[:10]:
                                        json = link

                        string_json = json.get_text()

                if 'coches.net' in url:
                        # print(soup)
                        # <div class="mt-AnimationFadeOut mt-ListAds-item mt-CardAd mt-CardBasic">
                        bloques = soup.select('.mt-Card-body')

                break 
                wd.quit()
