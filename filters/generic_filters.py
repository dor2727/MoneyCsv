from MoneyCsv.filters.base_filters import Filter
from MoneyCsv.filters.content_filters import *
from MoneyCsv.filters.filter_utils import join_filters_with_or
from MoneyCsv.filters.time_filters import *
from MoneyCsv.parsing import DescriptionDetailsParser_Friends , \
							 DescriptionDetailsParser_Location

# find str in either group or description
class StrFilter(Filter):
	def __init__(self, string, case_sensitive=None, regex=False):
		self._group       = GroupFilter(      string,
			case_sensitive=case_sensitive, regex=regex
		)
		self._description = DescriptionFilter(string,
			case_sensitive=case_sensitive, regex=regex
		)

		self._multi = self._group | self._description

		self.string = string
		self.case_sensitive = case_sensitive
		self.regex = regex

	def filter(self, data):
		return self._multi.filter(data)

	def __repr__(self):
		return self._multi.__repr__()

# auto classify which filter to use
class AutoFilter(Filter):
	_not_filter_prefix = ('~', '!')

	def __init__(self, string, case_sensitive=None, force_regex=False):
		string, exclude, regex, friends, location = self._preprocess_string(string, force_regex)

		if friends:
			self._filter = join_filters_with_or(
				FriendFilter(friend,
					case_sensitive=case_sensitive
				) for friend in friends
			)

		elif location:
			self._filter = LocationFilter(location, case_sensitive=case_sensitive)

		elif string[0] in ('<', '>'):
			self._filter = AmountFilter(string)

		elif string.islower():
			self._filter = DescriptionFilter(string,
				case_sensitive=case_sensitive, regex=regex
			)

		elif string[0].isupper():
			self._filter = GroupFilter(string,
				case_sensitive=case_sensitive, regex=regex
			)

		else:
			self._filter = StrFilter(string,
				case_sensitive=case_sensitive, regex=regex
			)


		if exclude:
			self._filter = NotFilter(self._filter)

	def _preprocess_string(self, string, force_regex):
		# check for regex
		regex = ('\\' in string) or force_regex

		# check whether this will be a NotFilter
		if not regex and string[0] in self._not_filter_prefix:
			exclude = True
			string = string[1:]
		elif   regex and string[0] == '~':
			# '!' is a special char for regex, '~' is not, thus, only '~' is allowed for regex exclude
			exclude = True
			string = string[1:]
		else:
			exclude = False

		# extract friends
		if regex:
			friends = False
		else:
			friends = DescriptionDetailsParser_Friends.extract_values_from_string(string)

		# extract location
		if regex:
			location = False
		else:
			location = DescriptionDetailsParser_Location.extract_values_from_string(string)

		if not string:
			raise ValueError("AutoFilter got empty string")

		return string, exclude, regex, friends, location

	def filter(self, data):
		return self._filter.filter(data)

	def __repr__(self):
		return self._filter.__repr__()


class AutoTimeFilter(BaseTimeFilter):
	"""
	input type:
		dict
			"year" = int or "current"
			"month" = int or "current"

			if only year - get the whole year
			if only month - get the last occurence of that month
			if both - get that specific month
		tuple
			(
				datetime start,
				datetime stop,
				bool start_inclusive optional,
				bool stop_inclusive optional
			)

		int
			get last n days
	"""
	def __init__(self, arg):
		self.arg = arg

		if type(arg) is dict:
			if "year" not in arg or type(arg["year"]) is not int:
				raise ValueError("Invalid input type")

			if "month" in arg:
				if type(arg["month"]) is not int:
					raise ValueError("Invalid input type")
				self._filter = TimeFilter_Month(*arg)
			else:
				self._filter = TimeFilter_Year(*arg)

		elif type(arg) is tuple:
			self._verify_time_range_tuple(arg)
			self._filter = TimeFilter_DateRange(*arg)

		elif type(arg) is int:
			self._filter = TimeFilter_Days(abs(int(arg)))

		else:
			raise ValueError("Unknown input type")

	def _verify_time_range_tuple(self, time_range_tuple):
		# verify input
		if len(time_range_tuple) < 2 or len(time_range_tuple) > 4:
			raise ValueError("Invalid input type")
		if type(time_range_tuple[0]) is not datetime.datetime:
			raise ValueError("Invalid input type")
		if type(time_range_tuple[1]) is not datetime.datetime:
			raise ValueError("Invalid input type")
		if len(time_range_tuple) > 2 and type(time_range_tuple[2]) is not bool:
			raise ValueError("Invalid input type")
		if len(time_range_tuple) > 3 and type(time_range_tuple[3]) is not bool:
			raise ValueError("Invalid input type")

	def filter(self, data):
		return self._filter.filter(data)

	def __repr__(self):
		return self._filter.__repr__()

	@property
	def _selected_time(self):
		return self._filter._selected_time
