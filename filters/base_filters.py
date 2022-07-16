import operator
import itertools
from collections.abc import Iterable

from MoneyCsv.consts import DEFAULT_SELECTED_TIME
from MoneyCsv.parsing import DataItem

class Filter(object):
	def filter(self, data):
		raise NotImplemented

	def get_filtered_data(self, data):
		return list(itertools.compress(data, self.filter(data)))

	@property
	def selected_time(self):
		return getattr(self, "_selected_time", DEFAULT_SELECTED_TIME)

	def __mod__(self, other):
		# verify input
		if not isinstance(other, Iterable):
			raise TypeError(f"unsupported operand type(s) for %: '{self.__class__}' and '{type(other)}'")

		# before the following check, verify that the list is not empty:
		if len(other) == 0:
			# return the same thing, rather than an empty list, since `other` may be a tuple or something
			return other

		# Validates that the iterable's items are of type DataItem
		# 	Verify that this object has subscripts (i.e. a list/tuple/etc. Not a generator/filter/map/etc.)
		if hasattr(other, "__getitem__"):
			# Should check all the items, but there is currently no such case of a list with mixed types
			if not isinstance(other[0], DataItem):
				raise TypeError(f"unsupported operand type(s) for %: '{self.__class__}' and a '{type(other)} of {type(other[0])}'")
			# can also use this, in case of import-loop, not allowing this file to import DataItem
			# if other[0].__class__.__name__ != "DataItem":

		return self.get_filtered_data(other)

	def __and__(self, other):
		return MultiFilter(self, other, "and")

	def __xor__(self, other):
		return MultiFilter(self, other, "xor")

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

_OPERATOR_MAP = {
	"and": operator.and_,
	"or": operator.or_,
	"xor": operator.xor,
}
class MultiFilter(Filter):
	"""docstring for MultiFilter"""
	def __init__(self, filter_1, filter_2, operation):
		self.filter_1 = filter_1
		self.filter_2 = filter_2

		self.operation = operation
		try:
			self.operator = _OPERATOR_MAP[operation.lower()]
		except KeyError as exc:
			allowed_operations = ", ".join(map("\"{}\"",format, _OPERATOR_MAP))
			raise ValueError(f"invalid operation! please use either {allowed_operations}") from exc

	def filter(self, data):
		return map(
			self.operator,
			self.filter_1.filter(data),
			self.filter_2.filter(data)
		)

	def __repr__(self):
		return f"({repr(self.filter_1)}) {self.operation} ({repr(self.filter_2)})"

	@property
	def _selected_time(self):
		if hasattr(self.filter_1, "_selected_time") and hasattr(self.filter_2, "_selected_time"):
			return f"({self.filter_1._selected_time} {self.operation} {self.filter_2._selected_time})"
		elif hasattr(self.filter_1, "_selected_time"):
			return self.filter_1._selected_time
		elif hasattr(self.filter_2, "_selected_time"):
			return self.filter_2._selected_time
		else:
			return DEFAULT_SELECTED_TIME

	# Todo: maybe I don't need this:
	@property
	def total_time(self):
		if hasattr(self.filter_1, "total_time") and hasattr(self.filter_2, "total_time"):
			return self.filter_1.total_time + self.filter_2.total_time
		elif hasattr(self.filter_1, "total_time"):
			return self.filter_1.total_time
		elif hasattr(self.filter_2, "total_time"):
			return self.filter_2.total_time
		else:
			print("[!] Warning: called `MultiFilter.total_time`, where both filters don't have `total_time`")
			return 0


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
