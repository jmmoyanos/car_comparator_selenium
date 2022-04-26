
#!/bin/bash -x

echo "build dockers local images for arm64 standalone chrome"
# build images for node-chrome for arm
cd docker-seleniarm
sh ./build.sh arm64 
cd ..
# docker compose up containers 
echo "docker compose up"
docker-compose up -d 

sleep 30

echo "flexicar"

docker exec car_cormparator_scraper_1 python main.py -r docker -s flexicar

sleep 5 

echo "mobile_de"

docker exec car_cormparator_scraper_1 python main.py -r docker -s mobile_de

# docker down

docker-compose down