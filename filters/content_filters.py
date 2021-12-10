import re
import operator

from MoneyCsv.filters.base_filters import Filter
from MoneyCsv.filters.filter_utils import find_string_in_string, find_string_in_list


# do not use this class directly - it is a meta class
class BaseContentFilter(Filter):
	def __init__(self, string_to_find, case_sensitive=None, regex=None):
		self.case_sensitive = case_sensitive if type(case_sensitive) is bool else True
		self.regex          = regex          if type(regex)          is bool else False

		if self.case_sensitive:
			self.string_to_find = string_to_find
		else:
			self.string_to_find = string_to_find.lower()

	def __repr__(self):
		return f"{self.__class__.__name__}({self.string_to_find})"

	def filter(self, data):
		raise NotImplemented

	def _find_string_in_string(self, string_to_search_in):
		return find_string_in_string(
			self.string_to_find,
			string_to_search_in,
			self.regex,
			self.case_sensitive
		)

	def _find_string_in_list(self, list_to_search_in):
		return find_string_in_list(
			self.string_to_find,
			list_to_search_in,
			self.regex,
			self.case_sensitive
		)


class DescriptionFilter(BaseContentFilter):
	def filter(self, data):
		return [
			self._find_string_in_string(i.description)
			for i in data
		]

class GroupFilter(BaseContentFilter):
	def filter(self, data):
		return [
			self._find_string_in_string(i.group)
			for i in data
		]

class FriendFilter(BaseContentFilter):
	def filter(self, data):
		return [
			self._find_string_in_list(i.friends)
			for i in data
		]

class CurrencyFilter(BaseContentFilter):
	def filter(self, data):
		return [
			i.currency == self.string_to_find
			for i in data
		]

# Filters whether there is a location set
class HasLocationFilter(Filter):
	def filter(self, data):
		return [
			bool(i.location)
			for i in data
		]

class LocationFilter(BaseContentFilter):
	def filter(self, data):
		return [
			(
				bool(i.location)
				and
				self._find_string_in_string(i.location)
			)
			for i in data
		]


# Filters whether there are extra_details in the DataItem
class HasExtraDetailsFilter(Filter):
	def filter(self, data):
		return [
			bool(i.extra_details)
			for i in data
		]

# Filters whether there is a specific extra_details key in the DataItem
class ExtraDetailsFilter(BaseContentFilter):
	def filter(self, data):
		return [
			(
				bool(i.extra_details)
				and
				self._find_string_in_list(list(i.extra_details.keys()))
			)
			for i in data
		]

# Filters whether there is a specific extra_details value to a certain key in the DataItem
class ExtraDetailsValueFilter(BaseContentFilter):
	def __init__(self, string_to_find, extra_details_name, case_sensitive=False, regex=False):
		super().__init__(string_to_find, case_sensitive, regex)

		if self.case_sensitive:
			self.extra_details_name = extra_details_name
		else:
			self.extra_details_name = extra_details_name.lower()

	def filter(self, data):
		return [
			(
				bool(i.extra_details)
				and
				find_string_in_list(
					self.extra_details_name, # string to find
					list(i.extra_details.keys()), #list_to_search_in
					self.regex,
					self.case_sensitive
				)
				and
				self._find_string_in_list(i.extra_details[self.extra_details_name])
			)
			for i in data
		]


class AmountFilter(Filter):
	def __init__(self, string, absolute_value=True):
		self.absolute_value = absolute_value

		if type(string) is str and string[0] == '<':
			self._action = "maximum"
			self.amount = self._float(string[1:])
		elif type(string) is str and string[0] == '>':
			self._action = "minumum"
			self.amount = self._float(string[1:])
		else: # default
			self._action = "maximum"
			self.amount = self._float(string)

	def _float(self, value):
		if self.absolute_value:
			return abs(float(value))
		else:
			return float(value)

	@property
	def _operator(self):
		if self._action == "maximum":
			return operator.ge
		elif self._action == "minimum":
			return operator.le
		else:
			raise ValueError(f"Invalid action ({self._action})")

	def filter(self, data):
		return [
			self._operator(self.amount, float(i))
			for i in data
		]

	def __repr__(self):
		return f"{self.__class__.__name__}({self._action} {self.amount} amount)"

