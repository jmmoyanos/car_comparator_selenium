#!/bin/bash -x

echo "0 0 * * * /root/car_comparator_selenium/scraper_server.sh" >> crontab_new
chmod +x crontab_new
crontab crontab_new