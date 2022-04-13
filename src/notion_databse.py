import notion_df
import pandas as pd
import os


if __name__ == "__main__":
    
    api_key= "secret_ykCuAA7S3BWsmQx7ueDXFcN68K8tVW6uBebjWmC8mAt"
    page_url= "https://www.notion.so/jmmoyano/050ad6eb764f4ebb901c306130732ce4?v=b44d2356140c4eb89b92cfba6cc113a0"

    notion_df.pandas() #That's it!

    df = pd.read_notion(page_url, api_key="secret_ykCuAA7S3BWsmQx7ueDXFcN68K8tVW6uBebjWmC8mAt").drop_duplicates().loc[1:]
