import argparse
from email.policy import default
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--site",
    help="website namesto scrape second hand cars separated by ,",
    default=['flexicar,mobile_de']
)
parser.add_argument(
    "-r",
    "--runtime",
    help="selenium runs on local machine or in docker selenium grid chrome standalone",
    required=True,
    default='local'
)
parser.add_argument(
    "-n",
    "--num_workers",
    help="num of multiple nodes making request in multithreading",
    default=4,
    required=False
)

parser.add_argument(
    "-st",
    "--storage",
    help="Batch size of links pages scraped simultaneously.",
    required=False,
    default="local"
)

now = datetime.now() 
datetime_string = str(now.strftime("%Y%m%d"))

logpath = './logs/'    
filename=f'scraper_{datetime_string}.log'
logging.basicConfig(handlers=[RotatingFileHandler(filename=logpath+filename,
                     mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                     format='%(levelname)s %(asctime)s %(message)s', 
                    datefmt='%m/%d/%Y%I:%M:%S %p')
     
logger = logging.getLogger('my_logger')

args = parser.parse_args()

print(args.runtime)

if 'flexicar' in args.site:
    from src.scrapers.es.flexicar import get_data_adds,get_links_cars,get_master
    print("flexicar")
    print("master")
    get_master.main(args.runtime,int(args.num_workers),logger, args.storage)
    print("links")
    get_links_cars.main(args.runtime,int(args.num_workers),logger, args.storage)
    print("data")
    get_data_adds.main(args.runtime,int(args.num_workers),logger, args.storage)

if 'mobile_de' in args.site:
    from src.scrapers.de.mobile_de import get_data_adds,get_links_cars,get_master
    print("mobile_de")
    print("master")
    get_master.main(args.runtime,logger, args.storage)
    print("links")
    get_links_cars.main(args.runtime,int(args.num_workers),logger, args.storage)
    print("data")
    get_data_adds.main(args.runtime,int(args.num_workers),logger, args.storage )

