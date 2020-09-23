import os
import re
import datetime

DEFAULT_DATA_DIRECTORY = os.path.expanduser("~/Dropbox/Projects/Money/data")
POSSIBLE_FILE_EXTENSIONS = [".mcsv", ".csv", ".txt", ""]

# 01/01/01 is Monday
DAYS = [datetime.datetime(1,1,i).strftime("%a") for i in range(1,7+1)]
# headers to look for in every csv
BASE_HEADERS = ["Date", "Amount", "Subject", "Description"]
# how to format [from_day - to_day]
DATE_REPRESENTATION_PATTERN = "%04d/%02d/%02d - %04d/%02d/%02d"


# PATTERN_WITH = "(?<=with )(.*?)(?=\\s[@\\(]|$)"
# a name starts with a capital letter
#    I write full names without spaces
_cappital_word = "[A-Z][A-Za-z]*"
# names list is
#     Name Name Name and Name
#     which is - at least one
#         where the last one (if there is more than one) follows "and"
#         and any name which is not the first nor the last has space before and after itself
_names_list  = "((%s)( %s)*( and %s)*)" % (tuple([_cappital_word])*3)
PATTERN_WITH = re.compile("(?<=with )" + _names_list)
PATTERN_FOR  = re.compile("(?<=for )"  + _names_list)
