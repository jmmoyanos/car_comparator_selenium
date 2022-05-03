
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
docker-compose build
docker-compose up -d 

sleep 25

echo "flexicar"

docker exec car_cormparator-scraper-1 python main.py -r docker -s flexicar

sleep 5 

echo "mobile_de"

docker exec car_cormparator-scraper-1 python main.py -r docker -s mobile_de

# docker down

docker-compose down --volumes --rmi all