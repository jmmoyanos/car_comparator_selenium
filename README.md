# Car Comparator of second hand cars

## Explanation

This project aims to find the differences in price and quality of used cars.

The idea is to scrape several second hand car websites, the main players in each country, in order to see if buying a car in germany is currently cheaper than buying it in spain.

### 🏗️ Tools

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=darkgreen)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

### ☁️ Cloud Storage

![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)

### Control Comparator database

[Notion Database](https://jmmoyano.notion.site/Cars_comparator-9f00a3afd5ed40ac99145f3560923bd6)

This database its hosted in notion and have the following columns to add the cars to the comparation list with some filters

- Name : Brand and type
- price_min
- price_max
- km_min
- km_max
- year_min
- year_max
- webs:  multiselect of webs to scrap

###  Webs to Scrap

 List of webs implemented:

- Country Germany :  [modile.de](https://www.mobile.de/?lang=en)
- Country Spain : [flexicar](https://www.flexicar.es/coches-segunda-mano/)
- Country Spain: [wallapop](https://es.wallapop.com/coches-segunda-mano)

## Getting Started

### Prerequisites

- Python 3.8
- Tested only on Mac M1

### Environment

I recommend to install the dependencies in a virtualenv. (I used conda)

```bash
conda create --name car_env python=3.8
conda activate car_env  
```

```bash
pip install -r requirements.txt
```

### Config Google Storage Secrets

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/client_secrets.json"
export GOOGLE_APPLICATION_CREDENTIALS="/root/car_cormparator/src/secrets/client_secrets.json"

```

### Run the application

```bash
python main.py
```

 or to specify the site put the sites separated by ,

 ```bash
python main.py --site flexicar,mobile_de
```

## Docker

### ARM

For dockerizing selenium its used selenium-grid for ARM, because the app hase been developed in arm platform
repo [docker-selenium-arm](https://github.com/seleniumhq-community/docker-seleniarm.git)

To build the images, run build.sh from the root directory of this repo, and specify your architecture, either arm64, arm/v7, or amd64:

```bash
./build.sh arm64 
```

To start the container image, run:

```bash
docker run --rm -it -p 4444:4444 -p 5900:5900 -p 7900:7900 --shm-size 3g local-seleniarm/standalone-chromium:latest
```

### AMD and other

follow instructions [docker-selenium](https://github.com/SeleniumHQ/docker-selenium)

## TODOs

- [X] requirements versions
- [X] Google Storage
- [X] Mobile.de
- [X] flexicar
- [X] Dockerize
- [X] requirements update
- [X] async functions for multiple scrap request - links and data
- [X] improve main
- [x] logger mobile_de
- [ ] logger flexicar
- [ ] Transform and Load Data
- [ ] Wallapop

