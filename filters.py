"""
Filters are objects which get the data (as a list of DataItems), and returns only the relevant DataItems.

Each Filter object must implement a "filter" method.
	def filter(self, data):

	the return value is a list of boolean values.
	True  means "include this item"
	False means "exclude this item"

The reasoning behind returning a boolean list is for chaining Filters:
Logical operations, such as "and" and "or" may be applied in the following way:
	all_filters = (filter_1 & filter_2) | filter_3
Additionally, there is NotFilter, which reverses the value of the filter.
	not_filter_1 = ~filter_1
	not_filter_1 = NotFilter(filter_1)

After creating the required filter, it is used in the following way:
	filtered_data = filter_instance.get_filtered_data(list_of_data_items)
	# alternatively
	filtered_data = filter_instance % list_of_data_items

The availabe filters can be grouped into 2 categories:
Data Filters:
	they filter by the content of the DataItem

	- Description
	- Subject
	- Friend
	- Has Extra Details
	- Amount

	- Str
		finds an str either in the Description or in the Subject
	- Auto
		automatically determines whether to use Description, Subject, Friend, or Amount
		mainly used for CLI, since the user input is not known in advance.

Time Filters:
	they filter by the date of the DataItem

	- Days
		returns items from the last N days (including today)
	- Today
		Days(1)
	- This Week
		Days(7)
	- Year
	- Month
	- DateRange
		gets a tuple of 2 Datetime objects, and returns objects which take place between the 2 Datetime objects
	- Auto
		automatically determines whether to use Days, DateRange, Year, or Month

"""

import datetime
import calendar

import operator
import itertools

class Filter(object):
	def filter(self, data):
		raise NotImplemented

	def get_filtered_data(self, data):
		return list(itertools.compress(data, self.filter(data)))

	def get_selected_time(self):
		return getattr(self, "_selected_time", "All time")

	def __mod__(self, other):
		# verify input
		if type(other) is not list:
			raise ValueError("modulo not defined for filter and non-list object")
		# Should check all the items
		if other[0].__class__.__name__ != "DataItem":
			raise ValueError("modulo is only defined for filter and a list of DataItem elements")

		return self.get_filtered_data(other)

	def __and__(self, other):
		return MultiFilter(self, other, "and")

	def __or__(self, other):
		return MultiFilter(self, other, "or")

	def __invert__(self):
		"""
		returns a Not Filter for this object
		syntax: ~obj
		"""
		return NotFilter(self)

	def __repr__(self):
		return self.__class__.__name__

class MultiFilter(Filter):
	"""docstring for MultiFilter"""
	def __init__(self, filter_1, filter_2, operation):
		self.filter_1 = filter_1
		self.filter_2 = filter_2

		self.operation = operation
		if operation.lower() == "and":
			self.operator = operator.and_
		elif operation.lower() == "or":
			self.operator = operator.or_
		else:
			raise ValueError("invalid operation! please use either \"and\" or \"or\"")

	def filter(self, data):
		return map(
			self.operator,
			self.filter_1.filter(data),
			self.filter_2.filter(data)
		)

	def __repr__(self):
		return f"({self.filter_1.__repr__()}) {self.operation} ({self.filter_2.__repr__()})"

	@property
	def _selected_time(self):
		if hasattr(self.filter_1, "_selected_time") and hasattr(self.filter_2, "_selected_time"):
			return f"({self.filter_1._selected_time} {self.operation} {self.filter_2._selected_time})"
		elif hasattr(self.filter_1, "_selected_time"):
			return self.filter_1._selected_time
		elif hasattr(self.filter_2, "_selected_time"):
			return self.filter_2._selected_time
		else:
			return 'All time'

class NotFilter(Filter):
	def __init__(self, filter_obj):
		self.filter_obj = filter_obj

	def filter(self, data):
		return map(
			operator.not_,
			self.filter_obj.filter(data),
		)

	def __repr__(self):
		return f"not ({self.filter_obj.__repr__()})"

# used for debug purpose
class TrueFilter(Filter):
	def filter(self, data):
		return [True] * len(data)
class FalseFilter(Filter):
	def filter(self, data):
		return [False] * len(data)


