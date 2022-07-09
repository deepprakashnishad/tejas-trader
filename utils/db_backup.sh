#!/bin/sh
DIR=`date +%m%d%y`
DEST=/media/deep/Projects/PythonProjects/KiteAutoTrader/db_backups/$DIR
mkdir $DEST

python /media/deep/Projects/PythonProjects/KiteAutoTrader/feeds/nse_derivative_loader.py

mongodump --host "localhost:27017" -d "quantTrader" -o $DEST