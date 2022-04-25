import yaml
from google.cloud import storage
import pandas as pd
import notion_df
import os.path
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
    df = pd.read_notion(page_url, api_key=secrets).drop_duplicates().drop('webs', axis=1)
    # df = df[df['webs'].str.contains(name)].drop('webs', axis=0)

    return df