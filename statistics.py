import re
import json
import numpy as np
import matplotlib.pyplot as plt

from MoneyCsv.consts import *
from MoneyCsv.money_utils import *
from MoneyCsv.filters import *

"""
TODO
group by:
	friends
	weekday
group by:
	amount of money
	amout of transactions
plot:
	bar
	pie
	text
"""


class Stats(object):
	def __init__(self, data, selected_time="All times"):
		self.data = data
		
		if len(selected_time) > 33:
			self.selected_time = "Multiple Time Filters"
		else:
			self.selected_time = selected_time

	@property
	def time_representation_str(self):
		if self.data:
			date_representation = DATE_REPRESENTATION_PATTERN % (
				*get_ymd_tuple(self.data[0].date),
				*get_ymd_tuple(self.data[-1].date),
			)
		else:
			date_representation = "no days found"

		try:
			amount_of_days = (self.data[-1].date - self.data[0].date).days + 1
		except:
			amount_of_days = 0

		return "%s [%s] (found %d days)" % (
			self.selected_time,
			date_representation,
			amount_of_days
		)

	def get_stats_dict(self):
		"return a dictionary"
		raise NotImplemented()

	def get_stats_list(self):
		"""
		return 2 lists - headers & values
		return them sorted
		"""
		raise NotImplemented()

	def to_text(self):
		raise NotImplemented()

	def to_telegram(self):
		return self.to_text()

	def to_csv(self):
		items = self.get_stats_dict().items()
		# sort by keys
		items = sorted(items, key=lambda x: x[0])

		headers = [i[0] for i in items]
		values = [i[1] for i in items]
		headers, values = self.get_stats_list()
		return ','.join(headers) + '\n' + ','.join(values)

	def to_json(self):
		return json.dumps(self.get_stats_dict(), sort_keys=True)

	def to_pie(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the pie chard
		if save is str: save the image to that path
		if save is True: save to the default location
		"""
		raise NotImplemented()

	def to_bar(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the bar graph
		if save is str: save the image to that path
		if save is True: save to the default location
		"""
		raise NotImplemented()

	def __repr__(self):
		return self.__class__.__name__


class FilteredStats(Stats):
	def get_stats_dict(self):
		amount_of_transactions = len(self.data)
		amount_of_money        = sum(map(float, self.data))

		if amount_of_money == 0:
			transactions_per_day = 0
			money_percentage = 0
		else:
			days = (self.data[-1].date - self.data[0].date).days + 1
			transactions_per_day = amount_of_transactions / days

			money_percentage = amount_of_money / amount_of_money

		if amount_of_transactions == 0:
			transaction_average = 0
		else:
			transaction_average = amount_of_money / amount_of_transactions

		return {
			"amount_of_transactions": amount_of_transactions,
			"amount_of_money": amount_of_money,
			"money_percentage": money_percentage,
			"transaction_average": transaction_average,
			"transactions_per_day": transactions_per_day,
		}

	def get_stats_list(self):
		stats = self.get_stats_dict()
		return tuple(zip(*stats.items()))

	def to_text(self):
		stats = self.get_stats_dict()

		s  = self.time_representation_str
		s += "\n"
		s += f"  transactions per day = {stats['transactions_per_day']:.2f}"
		s += "\n"
		s += "    (%3d) : %9.2f (%6.2f%%) ; item average %9.2f" % (
			stats["amount_of_transactions"],
			stats["amount_of_money"],
			stats["money_percentage"],
			stats["transaction_average"],
		)

		return s

class GroupedStats(Stats):
	_allowed_group_values = ("money", "money_average", "transactions")
	_allowed_sorting_methods = ("alphabetically", "by_value")

	def __init__(self, data, selected_time="All times", group_value="money", sort="by_value"):
		self.data = data
		self.selected_time = selected_time

		self.group_value = group_value.lower()
		if self.group_value not in self._allowed_group_values:
			raise ValueError("invalid group_value: %s" % group_value)

		self._sorting_method = sort.lower()
		if self._sorting_method not in self._allowed_sorting_methods:
			raise ValueError("invalid sorting_method: %s" % sort)

		self.values_dict = {}

	#
	def _get_headers(self):
		"""
		return list
		and creates self._headers for caching
		"""
		raise NotImplemented()

	@property
	def headers(self):
		if hasattr(self, "headers_sorted"):
			return self.headers_sorted
		elif hasattr(self, "_headers"):
			return self._headers
		else:
			# create self._headers & sort them
			self.group()

			if hasattr(self, "headers_sorted"):
				return self.headers_sorted
			elif hasattr(self, "_headers"):
				return self._headers
			else:
				raise NameError("could not find headers")

	def _get_filtered_data_per_header(self, header):
		raise NotImplemented()

	def _set_value_of_header(self, header):
		items = self._get_filtered_data_per_header(header)

		self.values_dict[header] = {}
		self.values_dict[header]["amount_of_money"]        = amount_of_money        = sum(map(float, items))
		self.values_dict[header]["amount_of_transactions"] = amount_of_transactions = len(items)

		if items:
			self.values_dict[header]["transaction_average"] = amount_of_money / amount_of_transactions
		else:
			self.values_dict[header]["transaction_average"] = 0

	def _get_value_of_header(self, header):
		self._set_value_of_header(header)

		if self.group_value == "money":
			return self.values_dict[header]["amount_of_money"]
		elif self.group_value == "transactions":
			return self.values_dict[header]["amount_of_transactions"]
		elif self.group_value == "money_average":
			return self.values_dict[header]["transaction_average"]
		else:
			raise ValueError

	def _sort(self, headers, values):
		# if either headers or values are empty
		if not headers or not values:
			return headers, values

		z = zip(headers, values)
		if self._sorting_method == "alphabetically":
			# sort by header (str), alphabetically
			sorted_z = sorted(z, key=lambda i: i[0])
		elif self._sorting_method == "by_value":
			# money is a negative number (unless its an income)
			if "money" in self.group_value:
				sorted_z = sorted(z, key=lambda i: i[1], reverse=False)
			else:
				sorted_z = sorted(z, key=lambda i: i[1], reverse=True)
		else:
			raise ValueError("invalid sorting_method")
		# unpack the zip into headers and values
		h, v = list(zip(*sorted_z))
		return h, v

	def group(self):
		"""
		group self.data
		return 2 lists
		1) headers: each item is the name of the group
		2) values:  each item is a list with the items
		"""
		headers = self._get_headers()

		values = list(map(
			self._get_value_of_header,
			headers
		))

		self.headers_sorted, self.values_sorted = self._sort(headers, values)
		return self.headers_sorted, self.values_sorted

	#
	@property
	def title(self):
		return f"{self.__class__.__name__}({self.group_value}) - {self.selected_time}"

	def to_pie(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the pie chard
		if save is str: save the image to that path
		if save is True: save to the default location

		if save:
			return open handle to the file with the image
		"""

		# initializing values
		if headers is None:
			headers = self.headers_sorted
		if values is None:
			values = self.values_sorted
		if title is None:
			title = self.title

		# plotting initialization
		fig, ax = plt.subplots()

		def pct(value):
			# value is given as a percentage - a float between 0 to 100
			return f"{value:.2f}%"

		# making the pie chart
		ax.pie(values, labels=headers, autopct=pct)
		ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

		# titles & labels
		ax.set_title(title)
		fig.canvas.set_window_title(title)

		# plotting - save to file
		if save:
			if save is True:
				path = DEFAULT_PIE_PATH
			else:
				path = save

			fig.savefig(path)
			plt.close(fig)

			return open(path, "rb")
		# plotting - interactive
		else:
			fig.show()
			return None

	def to_bar(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the pie chard
		if save is str: save the image to that path
		if save is True: save to the default location

		if save:
			return open handle to the file with the image
		"""

		# initializing values
		if headers is None:
			headers = self.headers_sorted
		if values is None:
			values = self.values_sorted
		if title is None:
			title = self.title

		# plotting initialization
		fig, ax = plt.subplots()

		# making the bar graph
		x = np.arange(len(headers))  # the label locations
		width = 0.35  # the width of the bars
		rects = ax.bar(x, values, width)

		# titles & labels
		fig.canvas.set_window_title(title)
		ax.set_title(title)
		ax.set_ylabel(self.group_value)
		ax.set_xticks(x)
		ax.set_xticklabels(headers)

		# plotting
		if save:
			if save is True:
				path = DEFAULT_BAR_PATH
			else:
				path = save

			fig.savefig(path)
			plt.close(fig)

			return open(path, "rb")
		else:
			fig.show()
			return None

	#
	def _generate_to_text_statistics_per_header(self, header, header_format, amount_of_money):
		self._get_value_of_header(header)
		stats = self.values_dict[header]

		stats["money_percentage"] = 100.0 * stats["amount_of_money"] / amount_of_money

		return "    %-14s (%4d) : %9.2f (%6.2f%%) ; transaction average %9.2f" % (
			(header_format % header),
			stats["amount_of_transactions"],
			stats["amount_of_money"],
			stats["money_percentage"],
			stats["transaction_average"],
		)

	def _generate_to_text_footer(self, header_format, amount_of_transactions, amount_of_money):
		s  = "    " + '-'*57
		s += "\n"
		s += "    %-14s (%4d) : %9.2f" % (
			(header_format % "Total"),
			amount_of_transactions,
			amount_of_money,
		)
		return s

	def _generate_to_text_header(self, transactions_per_day):
		s  = self.time_representation_str
		s += "\n"
		s += f"  transactions per day = {transactions_per_day:.2f}"

		return s

	def to_text(self):
		"""
		TODO
		and create a wrapper
			self._value
			that brings the relevant one based on self.group_value

		clean this function
		"""

		# calculate statistics for the whole time period
		amount_of_transactions = len(self.data)
		amount_of_money = sum(map(float, self.data))

		if amount_of_transactions == 0:
			transactions_per_day = 0
		else:
			amount_of_days = (self.data[-1].date - self.data[0].date).days + 1
			transactions_per_day = amount_of_transactions / amount_of_days

		s = self._generate_to_text_header(transactions_per_day)

		if not amount_of_transactions:
			s += "\n    No items found :("
			return s

		# print per-header statistics
		header_format = "%%-%ds" % (max(map(len, self.headers), default=1) + 1)
		for h in self.headers:
			s += "\n"
			s += self._generate_to_text_statistics_per_header(h, header_format, amount_of_money)

		s += "\n"
		s += self._generate_to_text_footer(header_format, amount_of_transactions, amount_of_money)

		return s

class GroupedStats_Friend(GroupedStats):
	def _get_headers(self):
		# get all headers
		headers = set()
		for i in self.data:
			h = i.friends
			for f in h:
				headers.add(f)

		# return a list, sorted alphabetically
		self._headers = sorted(headers)
		return self._headers

	def _get_filtered_data_per_header(self, header):
		return FriendFilter(header).get_filtered_data(self.data)

class GroupedStats_Location(GroupedStats):
	def _get_headers(self):
		# get all headers
		headers = set()
		for i in self.data:
			headers.add(i.location)

		if None in headers:
			headers.remove(None)

		# return a list, sorted alphabetically
		self._headers = sorted(headers)
		return self._headers

	def _get_filtered_data_per_header(self, header):
		return LocationFilter(header).get_filtered_data(self.data)

class GroupedStats_Subject(GroupedStats):
	def _get_headers(self):
		# get all headers
		headers = set()
		for i in self.data:
			h = i.subject
			if not h:
				print("empty subject for: %s" % i)
			headers.add(h)

		# return a list, sorted alphabetically
		self._headers = sorted(headers)
		return self._headers

	def _get_filtered_data_per_header(self, header):
		return SubjectFilter(header).get_filtered_data(self.data)


class FilteredGroupedStats(GroupedStats):
	STRIPPING_REGEX = [
		# brackets
		" ?\\(.*?\\)",
		# friends
		" ?with %s" % PATTERN_NAMES_LIST,
		" ?for %s"  % PATTERN_NAMES_LIST,
		" ?to %s"   % PATTERN_NAMES_LIST,
		# at location
		PATTERN_LOCATION,

		# specific patterns
		" ?to friends"
		"\\s?\\?\\?\\?" # ???
	]
	
	def __init__(self, data, filter_obj, **kwargs):
		super().__init__(data, **kwargs)

		self._filter_obj = filter_obj

		self._initialize_data()

	def _initialize_data(self):
		self._original_data = self.data
		self.data = self._filter_obj % self.data

	def _strip(self, s):
		for r in self.STRIPPING_REGEX:
			s = re.sub(r, '', s)
		s = s.strip()
		if not s:
			return "<empty>"
		else:
			return s
	def _get_headers(self):
		# get all headers
		headers = set()

		for i in self.data:
			h = self._strip(i.description)
			if h == "<empty>":
				print("empty description for: %s" % i)
			headers.add(h)

		# return a list, sorted alphabetically
		self._headers = sorted(headers)
		return self._headers

	def _get_filtered_data_per_header(self, header):
		return list(filter(
			lambda i: header == self._strip(i.description),
			self.data
		))

class SubjectGroupedStats(FilteredGroupedStats):
	"""
	requires:
		self._category_name
	"""
	def __init__(self, data, category_name=None, **kwargs):
		self._category_name = getattr(self, "_category_name", category_name)
		filter_obj = SubjectFilter(self._category_name)

		super().__init__(data, filter_obj, **kwargs)

class GroupedStats_Games(SubjectGroupedStats):
	_category_name = "Gaming"

