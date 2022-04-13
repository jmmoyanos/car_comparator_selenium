import notion_df
import pandas as pd
import utils

def get_notion_database():

    secrets = utils.read_secrets_yaml()['notion']['NOTION_API_KEY']
    page_url=  utils.read_secrets_yaml()['notion']['page_url']
    notion_df.pandas()

    ## Read frame
    df = pd.read_notion(page_url, api_key=secrets).drop_duplicates()
    df['webs_split']= df['webs'].apply(lambda x : x.split(','))

    return df