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
    

    def read_file(self, path):
         return pd.read_csv(f'gs://{self.bucket_name}/{path}')




if __name__ == "__main__":
    
    bucket = GStorage('car_comparator')
    df = bucket.read_file('de/make_and_model_links.csv')
    df