#!/bin/bash -x

echo "0 0 * * * /Users/josemariamoyano/Documents/python_projects/car_cormparator/scraper.sh" >> crontab_new
chmod +x crontab_new
crontab crontab_new