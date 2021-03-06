import yaml
from google.cloud import storage
import pandas as pd
import notion_df
import os.path
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
from src.storage import GStorage
import glob



def read_secrets_yaml():

    with open(os.path.dirname(__file__) + '/secrets/secrets.yaml') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        secrets = yaml.load(file, Loader=yaml.FullLoader)

    return secrets

def get_notion_database(name):

    secrets = read_secrets_yaml()['notion']['NOTION_API_KEY']
    page_url= read_secrets_yaml()['notion']['page_url']
    notion_df.pandas()

    ## Read frame
    df = pd.read_notion(page_url, api_key=secrets).drop_duplicates()
    df = df[df['webs'].str.contains(name, regex=True)]

    return df.drop('webs', axis=1)


def start_driver_selenium(option):
    
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    if option == 'docker_local':
        
        driver = webdriver.Remote(
                desired_capabilities=DesiredCapabilities.CHROME,
                command_executor="http://127.0.0.1:4444/wd/hub",
                options=chrome_options
            )
    
    if option == 'docker':
        
        driver = webdriver.Remote(
                desired_capabilities=DesiredCapabilities.CHROME,
                command_executor="http://selenium-hub:4444/wd/hub",
                options=chrome_options
            )
    
    elif option=='local':
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    
    return driver


def write_csv(type_, df,path,bucket=None):
    if type_ == 'local':
        path_dir = path.split('/')[:-1]
        path_dir = "/".join(path_dir)
        if not os.path.exists(path_dir):
            os.makedirs(path_dir)

        df.to_csv(path, encoding='utf-8', index=False)
    
    elif type_ == 'gstorage':
         bucket.write_csv_df(path,df)

def read_csv(type_, path, bucket=None):
    if type_ == 'local':
        return pd.read_csv(path, encoding='utf-8')
    
    elif type_ == 'gstorage':

         return bucket.read_csv(path)

def list_files(type_, path, bucket):

    if type_ == 'local':
        return glob.glob(str(str(path) + "*.csv"))

    elif type_ == 'gstorage':
         path = path.split('/')
         return  list(bucket.list_dir(path[1],path[2]))


def getBucket(type_):

    if type_ == 'local':
        return None
    elif type_ == 'gstorage':
        return  GStorage('car_comparator')


