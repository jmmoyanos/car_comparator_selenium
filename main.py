import argparse

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
    get_master.main(args.runtime)
    print("links")
    get_links_cars.main(args.runtime)
    print("data")
    get_data_adds.main(args.runtime)