#!/bin/bash
FOLDER=~/Projects/MoneyCsv
FILENAME="Visa.txt"
LOG=$FOLDER/daily_wget.log
LOG_NEW=$FOLDER/daily_wget.log.new
TEMP_LOCATION=$FOLDER/data/_latest

date > $LOG_NEW 2>&1
# For loop start (on $FILENAME)
~/Projects/Dropbox-Uploader/dropbox_uploader.sh download Projects/MoneyCsv/data/$FILENAME $TEMP_LOCATION >> $LOG_NEW 2>&1
echo moving $FILENAME >> $LOG_NEW 2>&1
mv $TEMP_LOCATION $FOLDER/data/$FILENAME >> $LOG_NEW 2>&1
# For loop end
cat $LOG_NEW >> $LOG
