import os
import re
import datetime

#
# Filesystem paths & extensions
#
DEFAULT_DATA_DIRECTORY = os.path.expanduser("~/Dropbox/Projects/MoneyCsv/data/by_type")
POSSIBLE_FILE_EXTENSIONS = [".mcsv", ".csv", ".txt", ""]
# temporary files
DEFAULT_PIE_PATH = "/tmp/pie.png"
DEFAULT_BAR_PATH = "/tmp/bar.png"


#
# Date
#
# how to format [from_day - to_day]
DATE_REPRESENTATION_PATTERN = "%04d/%02d/%02d - %04d/%02d/%02d"
#
DEFAULT_SELECTED_TIME = "All time"
#
NULL_DATE = datetime.datetime(1, 1, 1)
#
WEEK_STARTS_AT_SUNDAY = True
#
RETRY_SLEEP_AMOUNT_IN_HOURS = 1
RETRY_SLEEP_AMOUNT_IN_SECONDS = RETRY_SLEEP_AMOUNT_IN_HOURS * 60 * 60
