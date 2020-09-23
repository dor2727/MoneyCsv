import os
import re
import csv

from MoneyCsv.consts import *
from MoneyCsv.money_utils import *

import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

class DataItem(object):
	"""
	comment lines are either empty lines or lines starting with '#'

	expected input for __init__ is a list of items in the following order:
		date        (str) (yyyy/mm/dd)
		amount      (str) (float)
		subject     (str) (should start with a capital letter)
		description (str)

	the parsing should go as follows:
		first, this class should call each parser to store each value in its place
		then, the caller should iterate the 'reevaluate' method for each data object,
			with the previous data object
		this way, place holders such as "My date is the same as the previous object date"
			(which is written as "----/--/--") will be evaluated

	exported functions:
		__float__:
			return the amount of money
		__getitem__:
			return the items in the csv order
		friends:
			return a list of friends which were in the activity
		location:
			return a string of the location of the activity
		reevaluate:
			used for calling 2nd parsing functions
		is_fully_parsed:
			checks whether this object has finished parsing, and is in a valid state
		is_in_date_range:
			checks whether this object is contained within a date range

	"""
	_EXPECTED_HEADERS = [
		"Date",
		"Amount",
		"Subject",
		"Description",
	]

	def __init__(self, items, headers):
		assert(self._EXPECTED_HEADERS == headers)

		if self._check_if_comment(items):
			return

		if len(self._EXPECTED_HEADERS) != len(items):
			print(items)
		assert(len(self._EXPECTED_HEADERS) == len(items))

		self._items = []
		for i in range(len(self.PARSERS)):
			self._items.append(
				self.PARSERS[i](items[i])
			)

	def __getitem__(self, n):
		return self._items[n]

	def __repr__(self):
		return " : ".join(f() for f in self.FORMATTERS)
		
	def __float__(self):
		return self.amount
	# when __add__ is called (usually by calling `sum` on a list of DataItems), cast to float
	def __add__(self, other):
		if type(other) is DataItem:
			return float(self) + float(other)
		elif isinstance(other, (int, float)):
			return float(self) + other
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other

	def _check_if_comment(self, items):
		"""
		comment lines are either empty lines or lines starting with '#'
		"""
		if not items:
			# if items is an empty list - [] - then the line is empty
			self.is_comment = True
		elif items[0][0] == '#':
			self.is_comment = True
		else:
			self.is_comment = False

		return self.is_comment

	@property
	def friends(self):
		return find_friends_in_str(self.description, self.subject == "Friends")

	@property
	def location(self):
		return find_location_in_str(self.description)

	#
	# first parse iteration
	#
	def _parser_date(self, s):
		"""
		after this initial parsing, self.date will be:
			- str, if it was a special placeholder in the csv
			- datetime object, if it was a regular date value
		"""
		if s == COPY_LAST_DATE:
			self.date = COPY_LAST_DATE
		elif s == ADD_LAST_DATE:
			self.date = ADD_LAST_DATE
		else:
			self.date = datetime.datetime.strptime(s, "%Y/%m/%d")
		return self.date
	def _parser_amount(self, s):
		self.amount = float(s)
		return s
	def _parser_subject(self, s):
		self.subject = s
		return s
	def _parser_description(self, s):
		self.description = s

		# get both the word before the brackets, and the value of the brackets
		extra_details = re.findall("(\\w+)\\s+\\((.*?)\\)", s)
		if not extra_details:
			# TODO: maybe make it an empy dict instead of None
			self.extra_details = None
		else:
			self.extra_details = dict(extra_details)

		return s

	@property
	def PARSERS(self):
		"""
		returns a list of parsers by order
		"""
		return [
			self._parser_date,
			self._parser_amount,
			self._parser_subject,
			self._parser_description,
		]

	def _format_date(self):
		if type(self.date) is str:
			return self.date
		else:
			return self.date.strftime("%Y/%m/%d")
	def _format_amount(self):
		return f"{self.amount:.2f}"
	def _format_subject(self):
		return self.subject
	def _format_description(self):
		return self.description

	@property
	def FORMATTERS(self):
		"""
		returns a list of formatters by order
		"""
		return [
			self._format_date,
			self._format_amount,
			self._format_subject,
			self._format_description,
		]

	#
	# second parse iteration
	#
	def reevaluate(self, prev):
		if type(self.date) is str:
			if self.date == COPY_LAST_DATE:
				self.date = prev.date
			elif self.date == ADD_LAST_DATE:
				self.date = prev.date + datetime.timedelta(days=1)
	@property	
	def is_fully_parsed(self):
		"""
		checks whether every object has the type it is supposed to have
		"""
		return all([
			hasattr(self, "date"       ),
			hasattr(self, "amount"     ),
			hasattr(self, "subject"    ),
			hasattr(self, "description"),
		]) and all([
			type(self.date) is datetime.datetime,
			type(self.amount) is float,
			type(self.subject) is str,
			type(self.description) is str,
		])

	def is_in_date_range(self, start_date, end_date):
		return start_date <= self.date <= end_date

class DataItem_with_discount(DataItem):
	_EXPECTED_HEADERS = [
		"Date",
		"PreDiscount_Amount",
		"Amount",
		"Subject",
		"Description",
	]

	def _parser_prediscount_amount(self, s):
		self.prediscount_amount = float(s)
		return s
	@property
	def PARSERS(self):
		"""
		returns a list of parsers by order
		"""
		return [
			self._parser_date,
			self._parser_prediscount_amount,
			self._parser_amount,
			self._parser_subject,
			self._parser_description,
		]

	def _format_prediscount_amount(self):
		return f"{self.prediscount_amount:.2f}"
	@property
	def FORMATTERS(self):
		"""
		returns a list of formatters by order
		"""
		return [
			self._format_date,
			self._format_prediscount_amount,
			self._format_amount,
			self._format_subject,
			self._format_description,
		]


	@property	
	def is_fully_parsed(self):
		"""
		checks whether every object has the type it is supposed to have
		"""
		return all([
			hasattr(self, "date"              ),
			hasattr(self, "prediscount_amount"),
			hasattr(self, "amount"            ),
			hasattr(self, "subject"           ),
			hasattr(self, "description"       ),
		]) and all([
			type(self.date)               is datetime.datetime,
			type(self.prediscount_amount) is float,
			type(self.amount)             is float,
			type(self.subject)            is str,
			type(self.description)        is str,
		])


class DataFile(object):
	def __init__(self, file_path=None, data_item_class=DataItem, name=None):
		self._path = self.get_file_path(file_path)
		self._name = name or os.path.basename(file_path).capitalize()
		self._data_item_class = data_item_class
		self.reload()

	def __repr__(self):
		return "%s : %s : %d items" % (
			self.__class__.__name__,
			self._path,
			len(self.data)
		)

	@property
	def name(self):
		return self._name or "<no name>"
	

	def reload(self):
		self._load_data(self._path)
		self._reevaluate_data()
		self._create_titles()
		self._create_friends_list()
		self._create_locations_list()

	def get_file_path(self, file_path):
		# first, check in the main folder:
		full_file_path = os.path.join(
			DEFAULT_DATA_DIRECTORY,
			os.path.basename(file_path)
		)
		for e in POSSIBLE_FILE_EXTENSIONS:
			if os.path.exists(full_file_path + e):
				return full_file_path + e

		# else, check if its an absolute path
		if os.path.exists(file_path):
			return file_path

		# check if its an absolute path, or, if its a relative path that exists
		for e in POSSIBLE_FILE_EXTENSIONS:
			if os.path.exists(file_path + e):
				return file_path + e

		raise OSError("file not found (%s)" % file_path)

	def _load_data(self, path):
		r = csv.reader(
			open(
				os.path.expandvars(
					os.path.expanduser(
						path
					)
				)
			)
		)
		self.headers = next(r)
		self.data = list(filter(
			# filter out comment lines
			lambda x: not x.is_comment,
			map(
				# parse each line
				lambda x: self._data_item_class(x, self.headers),
				r
			)
		))

	def _reevaluate_data(self):
		for i in range(len(self.data[1:])):
			self.data[i+1].reevaluate(self.data[i])

	def _validate_data(self):
		invalid_items = [i for i in self.data if not i.is_fully_parsed()]
		return invalid_items or True

	def _create_titles(self):
		# iterate every item in the data, collect its subject into a unique list
		self.titles = list(set(i.subject for i in self.data))
		self.titles.sort()

	def _create_friends_list(self):
		all_friends = sum((i.friends for i in self.data), [])

		self.friends_histogram = counter(all_friends)
		# counter object is a list of tuples (name, amount)
		self.friends_histogram.sort(key=lambda x:x[1], reverse=True)

		self.friends = [i[0] for i in self.friends_histogram]

	def _create_locations_list(self):
		all_locations = [i.location for i in self.data if i.location]

		self.locations_histogram = counter(all_locations)
		# counter object is a list of tuples (name, amount)
		self.locations_histogram.sort(key=lambda x:x[1], reverse=True)

		self.locations = [i[0] for i in self.locations_histogram]

	@property
	def _data_range(self):
		return self.data[0].date, self.data[-1].date


class DataFileList(object):
	def __init__(self, *data_files):
		self.data_files = data_files

		self._set_items_origin()
		self._set_lists()

	def __repr__(self):
		return "%s : %s : %d files : %d items" % (
			self.__class__.__name__,
			self._path,
			len(self.data_files),
			len(self.data)
		)

	def _set_items_origin(self):
		for f in self.data_files:
			for d in f.data:
				d.origin = f.name

	def _set_lists(self):
		self.data = sum([i.data for i in self.data_files], [])

		self.data_file_latest = self.data_files[-1]
		self.data_latest = self.data_file_latest.data

		self.friends   = list(set(sum([i.friends for i in self.data_files], [])))
		self.locations = list(set(sum([i.locations for i in self.data_files], [])))


	def reload(self):
		for i in self.data_files:
			i.reload()

		self._set_items_origin()
		self._set_lists()

	def _validate_data(self):
		invalid_items = []
		res = True
		for i in self.data_files:
			temp = i._validate_data()
			if type(temp) is list:
				invalid_items += temp
			else:
				res &= temp
		return invalid_items or res

