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
    help="website namesto scrape second",
    choices=['flexicar', 'mobile_de']
)
parser.add_argument(
    "-r",
    "--runtime",
    help="selenium runs on local machine or in docker selenium grid chrome standalone",
    required=True,
    default='local',
    choices = ["docker","docker_local","local"]
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
    default="local",
    choices = ["local","gstorage"]
)

now = datetime.now() 
datetime_string = str(now.strftime("%Y%m%d"))

logpath = f'./logs/scraper_{datetime_string}.log'

logging.basicConfig(handlers=[RotatingFileHandler(filename=logpath,
                     mode='w', maxBytes=512000, backupCount=4)], level=logging.INFO,
                     format='%(levelname)s %(asctime)s %(message)s', 
                    datefmt='%m/%d/%Y%I:%M:%S %p')
     
logger = logging.getLogger('my_logger')

args = parser.parse_args()

print(args.runtime)

if 'flexicar' == args.site:
    from src.scrapers.es.flexicar import get_data_adds,get_links_cars,get_master
    try:
        logger.info(f'-----> flexicar - calling master')
        get_master.main(args.runtime,int(args.num_workers),logger, args.storage)
        logger.info(f'-----> flexicar - finish master')
        
    except Exception as exp:
        logger.error(f'-----> flexicar -  master {exp}')

    try:
        logger.info(f'-----> flexicar - calling links')
        get_links_cars.main(args.runtime,int(args.num_workers),logger, args.storage)
        logger.info(f'-----> flexicar - finish links')

    except Exception as exp:
        logger.error(f'-----> flexicar -  master {exp}')

    try:
        logger.info(f'-----> flexicar - calling data')
        get_data_adds.main(args.runtime,int(args.num_workers),logger, args.storage)
        logger.info(f'-----> flexicar - finish data')

    except Exception as exp:
        logger.error(f'-----> flexicar -  master {exp}')

if 'mobile_de' == args.site:
    from src.scrapers.de.mobile_de import get_data_adds,get_links_cars,get_master

    ## MASTER
    try:
        logger.info(f'-----> mobile_de - calling master')
        get_master.main(args.runtime,logger, args.storage)
        logger.info(f'-----> mobile_de - finish master')

    except Exception as exp:
        logger.error(f'-----> mobile_de -  master {exp}')

    ## LINKS
    try:
        logger.info(f'-----> mobile_de - calling links')
        get_links_cars.main(args.runtime,int(args.num_workers),logger, args.storage)
        logger.info(f'-----> mobile_de - finish links')

    except Exception as exp:
        logger.error(f'-----> mobile_de -  master {exp}')

    ##DATA

    try:
        logger.info(f'-----> mobile_de - calling data')
        get_data_adds.main(args.runtime,int(args.num_workers),logger, args.storage)
        logger.info(f'-----> mobile_de - finish data')

    except Exception as exp:
        logger.error(f'-----> mobile_de -  master {exp}')

