import os
import datetime

from collections import OrderedDict, Counter

from MoneyCsv.consts import *

#
# file utils
#
# get the newsest file
def newest(path=DEFAULT_DATA_DIRECTORY):
	files = os.listdir(path)
	paths = [os.path.join(path, basename) for basename in files]
	return max(paths, key=os.path.getctime)

#
# parsing utils
#
def ordered_unique(l):
	return list(OrderedDict.fromkeys(l))

def counter(data):
	return list(Counter(data).items())

#
# regex utils
#
def re_escape(x):
	return ''.join(
		(
			'\\'+i
			 if
			i in re.sre_parse.SPECIAL_CHARS
			 else
			i
		)
		for i in x
	)

def re_exact(x):
	return f"\\b{x}\\b"

#
# datetime utils
#
def get_ymd_tuple(d):
	"ymd stands for Year, Month, Day"
	return (d.year, d.month, d.day)

def get_midnight(d):
	return datetime.datetime(*get_ymd_tuple(d))

def seconds_to_str(n):
	n = int(n)

	s = ''

	days = (n // (60*60*24))
	if days:
		s += f"{days:3d} days"
	else:
		s += " " * (3+1+4)

	s += ' '

	hours = (n // (60*60) % (24))
	if hours:
		s += f"{hours:2d} hours"
	else:
		s += " " * (2+1+5)

	s += ' '

	minutes = (n // (60) % (60*24) % 60)
	if minutes:
		s += f"{minutes:2d} minutes"
	else:
		s += " " * (2+1+7)

	return s

def seconds_to_hours_str(n):
	h = n / (3600)
	return f"{h:.2f}"

def shorten_selected_time(selected_time):
	if len(selected_time) > 33:
		return "Multiple Time Filters"
	else:
		return selected_time

def format_dates(date1, date2):
	return DATE_REPRESENTATION_PATTERN % (
		*get_ymd_tuple(date1),
		*get_ymd_tuple(date2),
	)

#
# debug utils
#
def print_items(l, ret=False):
	if ret:
		return '\n'.join(i.__repr__() for i in l)
	else:
		print('\n'.join(i.__repr__() for i in l))
