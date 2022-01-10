from MoneyCsv.statistics.base_statistics import DetailedStatsFiltered
from MoneyCsv.statistics.extra_details_statistics import DetailedStats_ExtraDetailWithName
from MoneyCsv.filters import DescriptionFilter
from MoneyCsv.utils import re_exact

from functools import reduce

NO_EXTRA_DETAILS = "<no extra_details>"

class DetailedStats_Description(DetailedStatsFiltered):
	def __init__(
		self, data, description_text=None,
		time_filter=None, grouping_method="time", sorting_method="by_value",
		**filter_obj_kwargs,
	):
		self._set_filter_obj(description_text, **filter_obj_kwargs)

		super().__init__(data, self._filter_obj, time_filter, grouping_method, sorting_method)

		self._get_extra_details_name()

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

	def _set_filter_obj(self, description_text, **filter_obj_kwargs):
		self._description_text = getattr(self, "_description_text", description_text)
		self._filter_obj_kwargs = getattr(self, "_filter_obj_kwargs", filter_obj_kwargs)

		if self._description_text is None:
			raise ValueError("DetailedStats_Description received None as group name")

		self._filter_obj = DescriptionFilter(self._description_text, **self._filter_obj_kwargs)
		return self._filter_obj


	def _get_titles(self):
		titles = reduce(
			set.union,
			(set(i.extra_details[self._extra_details_name]) for i in self.data)
		) 
		titles.add(NO_EXTRA_DETAILS)

		# return a list, sorted alphabetically
		self._titles = sorted(titles)
		return self._titles

	def _get_items_of_title(self, title):
		if title == NO_EXTRA_DETAILS:
			return list(filter(
				lambda i: (not i.extra_details) or (i.extra_details and self._extra_details_name not in i.extra_details),
				self.data
			))
		else:
			return list(filter(
				lambda i: title in i.extra_details[self._extra_details_name],
				self.data
			))

	def _plot_make_pie_clickable(self, fig, patches):
		def onclick(event):
			# Get the patch and its label
			patch = event.artist
			label = patch.get_label()

			# Create a grouped-stats object for that label
			g = DetailedStats_ExtraDetailWithName(
				self._filter_obj,
				self._extra_details_name,
				self.data,
				time_filter=self._time_filter,
				grouping_method=self._grouping_method,
				sorting_method=self._sorting_method,
			)
			
			# Set title prefix
			g._title_prefix = getattr(self, "_title_prefix", '') + f"{self.__class__.__name__}({self._grouping_method}) / "


			print(f"=== {label} ===")
			print(g.to_text())
			g.to_pie(save=False)

		for patch in patches:
			if patch.get_label() == NO_EXTRA_DETAILS:
				continue
			patch.set_picker(True)

		fig.canvas.mpl_connect('pick_event', onclick)


class DetailedStats_Twitch(DetailedStats_Description):
	_group_name = re_exact("twitch")
	_filter_obj_kwargs = {"case_sensitive": True, "regex": True}
