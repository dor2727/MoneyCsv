import re


#
# File format
#
# headers to look for in every csv
BASE_HEADERS = ["Date", "Amount", "Group", "Description"]
ALLOWED_HEADERS = BASE_HEADERS + [
	"PreDiscount_Amount", # Amount before discoung

	"Payment", # How was this transaction payed - credic card, cash, etc.
	"Currency", # With which currency was this transaction payed
	"Amount_Converted", # Amount after converting from the currency

	"Frequency", # the frequency of automatic trasactions
]
# Date parsing
COPY_LAST_DATE             = "----/--/--"
ADD_LAST_DATE              = "----/--/+1"
SPECIAL_DATE_FORMATS       = [COPY_LAST_DATE, ADD_LAST_DATE]

# Files starting with '_'
FILE_EXCLUDE_PATTERN__HIDDEN     = re.compile("^\\.")
# Files starting with '.'
FILE_EXCLUDE_PATTERN__UNDERSCORE = re.compile("^\\_")
# Files having "weird" in their name
FILE_EXCLUDE_PATTERN__WEIRD      = re.compile(".*\\.weird\\..*")
# Files having "Vacation" in their path
FILE_EXCLUDE_PATTERNS = [
	FILE_EXCLUDE_PATTERN__HIDDEN,
	FILE_EXCLUDE_PATTERN__UNDERSCORE,
	FILE_EXCLUDE_PATTERN__WEIRD,
]
#
FOLDER_EXCLUDE_PATTERN__VACATION   = re.compile("/Vacations?/?")
FOLDER_EXCLUDE_PATTERNS = [
	FOLDER_EXCLUDE_PATTERN__VACATION,
]

#
# Extra details
#
EXTRA_DETAILS_SEPERATOR = " ; "
EXTRA_DETAILS_PATTERN_STRIP   = " ?\\(.*?\\)"
	# get both the word before the brackets, and the value of the brackets
EXTRA_DETAILS_PATTERN_EXTRACT = "(\\w+)\\s+\\((.*?)\\)"


#
# Friends
#
# a name starts with a capital letter. full names are written without space.
re_cappital_word = "[A-Z][A-Za-z]*"

# names list is
#     Name Name Name and Name
#     which is - at least one
#         where the last one (if there is more than one) is followed by "and"
#         and any name which is not the first nor the last has space before and after itself
PATTERN_NAMES_LIST  = "((%s)( %s)*( and %s)*)" % (tuple([re_cappital_word])*3)

FRIEND_PATTERN_WORDS = ["with", "for", "to"]

FRIEND_PATTERN_EXTRACT = [
	re.compile(f"(?<={word} ){PATTERN_NAMES_LIST}")
	for word in FRIEND_PATTERN_WORDS
]
FRIEND_PATTERN_STRIP = [
	re.compile(f" ?{word} {PATTERN_NAMES_LIST}")
	for word in FRIEND_PATTERN_WORDS
]
FRIEND_PATTERN_TO_FRIENDS = " to friends"


#
# Regex patterns - location
#
# a location will be wrapped by @ at both ends
# e.g.: go for a walk @ some place @
PATTERN_LOCATION = " ?@ ?(.*?) ?@"
PATTERN_LOCATION_THEIR_PLACE = "@@"


CURRENCY_SYMBOL = {
	"nis": '\u20aa',
	"euro": '\u20ac',
	"dollar": '$',
	"yan": '\xa5',
	"franc": 'f', # The official symbol is "FNC", but I want it as a single letter
}
CURRENCY_SYMBOL_NIS = CURRENCY_SYMBOL["nis"]
