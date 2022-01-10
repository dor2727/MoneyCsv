from MoneyCsv.statistics.base_statistics import DetailedStats
from MoneyCsv.filters import HasExtraDetailsFilter, \
							ExtraDetailsFilter, \
							ExtraDetailsValueFilter, \
							DescriptionFilter

from functools import reduce

# do not use this class directly - it is a meta class
class DetailedStats_ExtraDetails_Abstract(DetailedStats):
	"""
	requires:
		self._filter_obj
		self._extra_details_name

		and requires a call to self._initialize_data in __init__
			since it requires self._filter_obj
	"""
	def _initialize_data(self):
		self._original_data = self.data
		self.data = self._filter_obj % self.data


	def _get_titles(self):
		# get all headers
		titles = set()

		for i in self.data:
			t = i.extra_details[self._extra_details_name]
			if t:
				titles.update(t)

		# return a list, sorted alphabetically
		self._titles = sorted(titles)
		return self._titles

	def _get_items_of_title(self, title):
		return ExtraDetailsValueFilter(title, self._extra_details_name).get_filtered_data(self.data)

# extracts `extra_details_name` automatically
class DetailedStats_ExtraDetail(DetailedStats_ExtraDetails_Abstract):
	def __init__(self, search_filter, *args, **kwargs):
		# a bit of a weird flow

		# first, set the `data` and the rest of the __init__ flow
		super().__init__(*args, **kwargs)

		# next, create a _filter_obj
		self._filter_obj = (
			search_filter
			 &
			HasExtraDetailsFilter()
			 &
			~DescriptionFilter('&') # TODO: remove me. This is a patch since '&' is not parsed yet
		)
		# _filter_obj is used here for setting self.data to be the filtered data
		self._initialize_data()
		# using the filtered data, the extra_details_name is extracted
		self._get_extra_details_name()
		# now, the filter_object is further narrowed
		self._filter_obj &= ExtraDetailsFilter(self._extra_details_name)
		# and the data is being filtered, again
		self.data = self._filter_obj % self.data


	def _get_extra_details_name(self):
		# get all extra_details names
		names = reduce(
			set.union,
			(set(i.extra_details.keys()) for i in self.data)
		)


		# hopefully, the filter is specific enough, so that only one extra_details name was found
		if len(names) == 1:
			self._extra_details_name = list(names)[0]

		elif len(names) == 0:
			raise ValueError("No possible extra_details_name found")

		else:
			print(names)
			raise ValueError(f"Too many ({len(names)}) possible extra_details_name found")

		return self._extra_details_name

# used when `extra_details_name` is specified
class DetailedStats_ExtraDetailWithName(DetailedStats_ExtraDetails_Abstract):
	def __init__(self, search_filter, extra_details_name, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._extra_details_name = extra_details_name

		self._filter_obj = (
			search_filter
			 &
			ExtraDetailsFilter(self._extra_details_name)
		)

		self._initialize_data()
