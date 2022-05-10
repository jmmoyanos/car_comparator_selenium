# Imports the Google Cloud client library
from google.cloud import storage
import pandas as pd
# Instantiates a client
class GStorage():
    
    def __init__(self, bucket_name):
        storage_client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = storage_client.get_bucket(bucket_name)

    def write_file(self, path, name):
         blob = self.bucket.blob(name)
         blob.upload_from_filename(path)
    

    def read_csv(self, path):
         return pd.read_csv(f'gs://{self.bucket_name}/{path}', encoding='utf-8')
    
    def write_csv_df(self, file_name, df):
        self.bucket.blob(file_name).upload_from_string(df.to_csv(encoding='utf8', index=False), 'text/csv')
    
    def list_dir(self,name,path):
       lista= [i.path[3:] for i in list(self.bucket.list_blobs(prefix='data/'+name +'/')) if path in i.path]
       lista = [file[len(self.bucket_name)+3 :].replace("%2F", "/") for file in lista]
       return lista





# if __name__ == "__main__":
    
#     bucket = GStorage('car_comparator')
#     # df = pd.read_csv('../data/mobile_de/make_and_model_links.csv')
#     # df
    
#     # bucket.write_csv('elpepe.csv',df)
#     blobs_specific = list(bucket.list_dir('mobile_de','make_model_ads_links'))
#     dfs = [ bucket.read_file(path) for path in blobs_specific]
#     df = pd.concat(dfs)
