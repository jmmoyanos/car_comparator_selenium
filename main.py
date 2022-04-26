import argparse
import time

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
    "-bl",
    "--batch_links",
    help="Batch size of links pages scraped simultaneously.",
    required=False,
)
parser.add_argument(
    "-bd",
    "--batch_data",
    help="Batch size of cars to scrape",
    required=False,
)


time.sleep(30)
args = parser.parse_args()

print(args.runtime)

if 'flexicar' in args.site:
    from src.es.flexicar import get_data_adds,get_links_cars,get_master
    print("flexicar")
    print("master")
    get_master.main(args.runtime)
    print("links")
    get_links_cars.main(args.runtime)
    print("data")
    get_data_adds.main(args.runtime)

if 'mobile_de' in args.site:
    from src.de.mobile_de import get_data_adds,get_links_cars,get_master
    print("mobile_de")
    print("master")
    # get_master.main(args.runtime)
    # print("links")
    # get_links_cars.main(args.runtime)
    # print("data")
    get_data_adds.main(args.runtime)
