import os
import re
import datetime

DEFAULT_DATA_DIRECTORY = os.path.expanduser("~/Dropbox/Projects/MoneyCsv/data")
TELEGRAM_DATA_DIRECTORY = os.path.expanduser("~/Dropbox/Projects/MoneyCsv/Telegram_Bot/data")
POSSIBLE_FILE_EXTENSIONS = [".mcsv", ".csv", ".txt", ""]


DATE_FORMAT = "%Y/%m/%d"
COPY_LAST_DATE = "----/--/--"
ADD_LAST_DATE = "----/--/+1"

# PATTERN_WITH = "(?<=with )(.*?)(?=\\s[@\\(]|$)"
# a name starts with a capital letter
#    I write full names without spaces
re_cappital_word = "[A-Z][A-Za-z]*"
# names list is
#     Name Name Name and Name
#     which is - at least one
#         where the last one (if there is more than one) follows "and"
#         and any name which is not the first nor the last has space before and after itself
PATTERN_NAMES_LIST  = "((%s)( %s)*( and %s)*)" % (tuple([re_cappital_word])*3)
PATTERN_WITH = re.compile("(?<=with )" + PATTERN_NAMES_LIST)
PATTERN_FOR  = re.compile("(?<=for )"  + PATTERN_NAMES_LIST)
PATTERN_TO   = re.compile("(?<=to )"   + PATTERN_NAMES_LIST)
FRIEND_PATTERN = [PATTERN_WITH, PATTERN_FOR, PATTERN_TO]


# a location will be wrapped by @ at both ends
# e.g.: go for a walk @ some place @
PATTERN_LOCATION = " ?@ ?(.*?) ?@"
PATTERN_LOCATION_THEIR_PLACE = "@@"


DEFAULT_PIE_PATH = "/tmp/pie.png"
DEFAULT_BAR_PATH = "/tmp/bar.png"


WEEK_STARTS_AT_SUNDAY = True


EXTRA_DETAILS_SEPERATOR = " ; "
