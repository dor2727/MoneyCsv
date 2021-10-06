#!/bin/bash
PROJECT=MoneyCsv
FOLDER=~/Projects/$PROJECT
LOG=$FOLDER/daily_wget.log
LOG_NEW=$FOLDER/daily_wget.log.new
TEMP_LOCATION=$FOLDER/data/_latest

# Declare a string array with type
declare -a FileNameArray=(
	"cash.csv"
	"isracard.csv"
	"isracard.weird.csv"
	"italy_2019.mcsv"
	"japan_2017.csv"
	"japan_2017_details.csv"
	"Transactions.csv"
	"Visa_automat.csv"
	"Visa.txt"
	"Visa.weird.csv"
)

date > $LOG_NEW 2>&1

for FILENAME in "${FileNameArray[@]}"; do
  echo $FILENAME
  ~/Projects/Dropbox-Uploader/dropbox_uploader.sh download Projects/$PROJECT/data/$FILENAME $TEMP_LOCATION >> $LOG_NEW 2>&1
  echo moving $FILENAME >> $LOG_NEW 2>&1
  mv $TEMP_LOCATION $FOLDER/data/$FILENAME >> $LOG_NEW 2>&1
done

cat $LOG_NEW >> $LOG

