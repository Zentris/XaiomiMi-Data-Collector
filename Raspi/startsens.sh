#!/bin/bash

export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

cd /home/pi/homeautomat/xiaomi

echo "-----------------------------------------------------------"
echo `date` >> startsens.log

/home/pi/homeautomat/xiaomi/XiaomiMiReader.py >> startsens.log

