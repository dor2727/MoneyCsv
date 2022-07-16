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

	def _find_string_in_string(self, string_to_search_in, string_to_find=None):
		if string_to_find is None:
			string_to_find = self.string_to_find

		return find_string_in_string(
			string_to_find,
			string_to_search_in,
			self.regex,
			self.case_sensitive
		)

	def _find_string_in_list(self, list_to_search_in, string_to_find=None):
		if string_to_find is None:
			string_to_find = self.string_to_find

		return find_string_in_list(
			string_to_find,
			list_to_search_in,
			self.regex,
			self.case_sensitive
		)


class DescriptionFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return self._find_string_in_string(item.description)

class GroupFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return self._find_string_in_string(item.group)

class FriendFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return self._find_string_in_list(item.friends)

class CurrencyFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return item.currency == self.string_to_find

# Filters whether there is a location set
class HasLocationFilter(Filter):
	def _filter_single_item(self, item):
		return bool(item.location)

class LocationFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return (
			bool(item.location)
			and
			self._find_string_in_string(item.location)
		)


# Filters whether there are extra_details in the DataItem
class HasExtraDetailsFilter(Filter):
	def _filter_single_item(self, item):
		return bool(item.extra_details)

# Filters whether there is a specific extra_details key in the DataItem
class ExtraDetailsFilter(BaseContentFilter):
	def _filter_single_item(self, item):
		return (
			bool(item.extra_details)
			and
			# `item.extra_details` is a dict, but it can both be iterated over and has `in`
			self._find_string_in_list(item.extra_details)
		)

# Filters whether there is a specific extra_details value to a certain key in the DataItem
class ExtraDetailsValueFilter(BaseContentFilter):
	def __init__(self, string_to_find, extra_details_name, case_sensitive=False, regex=False):
		super().__init__(string_to_find, case_sensitive, regex)

		if self.case_sensitive:
			self.extra_details_name = extra_details_name
		else:
			self.extra_details_name = extra_details_name.lower()

	def _filter_single_item(self, item):
		return (
			bool(item.extra_details)
			and
			self._find_string_in_list(item.extra_details, self.extra_details_name)
			and
			self._find_string_in_list(item.extra_details[self.extra_details_name])
		)


_OPERATOR_MAP = {
	"maximum": operator.ge,
	"minimum": operator.le,
}
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

		try:
			self._operator = _OPERATOR_MAP[self._action]
		except KeyError as exc:
			allowed_operations = ", ".join(map("\"{}\"",format, _OPERATOR_MAP))
			raise ValueError(f"invalid operation! please use either {allowed_operations}") from exc


	def _float(self, value):
		if self.absolute_value:
			return abs(float(value))
		else:
			return float(value)

	def _filter_single_item(self, item):
		return self._operator(self.seconds, float(item))

	def __repr__(self):
		return f"{self.__class__.__name__}({self._action} {self.amount} amount)"

