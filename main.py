import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--site",
    help="names, to scrape web selling second hand cars separated by ,",
    required=True,
    default=['flexicar,mobile_de']
)


args = parser.parse_args()

if 'flexicar' in args.site:
    from src.es.flexicar import get_data_adds,get_links_cars,get_master
    get_master.main()
    get_links_cars.main()
    get_data_adds.main()

if 'mobile_de' in args.site:
    from src.de.mobile_de import get_data_adds,get_links_cars,get_master
    get_master.main()
    get_links_cars.main()
    get_data_adds.main()