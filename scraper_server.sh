
#!/bin/bash -x

# build images for node-chrome for arm
docker_chrome_arm=($(docker images | grep local-seleniarm/node-chromium))


if (( ${#docker_chrome_arm[@]} == 0 )); then
    echo "Need build the images" >&2
    echo "build dockers local images for arm64 standalone chrome"
    cd docker-seleniarm
    sh ./build.sh arm64 
    cd ..
fi

# docker compose up containers 
echo "docker compose up"
docker-compose -f docker-compose_server.yml build
docker-compose -f docker-compose_server.yml up -d 

sleep 25

echo "flexicar"

docker exec car_comparator_selenium_scraper_1 python main.py -r docker -s flexicar -n 3 -st gstorage

sleep 5 

echo "mobile_de"

docker exec car_comparator_selenium_scraper_1 python main.py -r docker -s mobile_de -n 3 -st gstorage

# docker down

docker-compose -f -f docker-compose_server.yml down
