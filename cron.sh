#!/bin/bash -x

echo "0 0 * * * /root/car_cormparator/scraper_server.sh" >> crontab_new
chmod +x crontab_new
crontab crontab_new