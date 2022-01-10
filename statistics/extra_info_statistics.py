from MoneyCsv.statistics.base_statistics import DetailedStats
from MoneyCsv.statistics.group_statistics import DetailedStats_Group
from MoneyCsv.filters import GroupFilter, FriendFilter, LocationFilter
from MoneyCsv.utils import re_exact

class DetailedStats_AllGroups(DetailedStats):
	def _get_titles(self):
		titles = set()

		for i in self.data:
			t = i.group
			if not t:
				print(f"empty group for: {i}")
			titles.add(t)

		# return a list, sorted alphabetically
		self._titles = sorted(titles)
		return self._titles

	def _get_items_of_title(self, title):
		return GroupFilter(re_exact(title), case_sensitive=True, regex=True).get_filtered_data(self.data)

	def _plot_make_pie_clickable(self, fig, patches):
		def onclick(event):
			# Get the patch and its label
			patch = event.artist
			label = patch.get_label()

			# Create a grouped-stats object for that label
			g = DetailedStats_Group(
				self.data,
				group_name=re_exact(label),
				time_filter=self._time_filter,
				grouping_method=self._grouping_method,
				sorting_method=self._sorting_method,
				case_sensitive=False, regex=True,
			)

			# Set title prefix
			g._title_prefix = getattr(self, "_title_prefix", '') + f"{self.__class__.__name__}({self._grouping_method}) / "


			print(f"=== {label} ===")
			print(g.to_text())
			g.to_pie(save=False)

		for patch in patches:
			patch.set_picker(True)

		fig.canvas.mpl_connect('pick_event', onclick)

class DetailedStats_Friend(DetailedStats):
	def _get_titles(self):
		titles = set()

		for i in self.data:
			if i.friends:
				titles.update(i.friends)

		# return a list, sorted alphabetically
		self._titles = sorted(titles)
		return self._titles

	def _get_items_of_title(self, title):
		return FriendFilter(title).get_filtered_data(self.data)

class DetailedStats_Location(DetailedStats):
	def _get_titles(self):
		titles = set()

		for i in self.data:
			titles.add(i.location)

		if None in titles:
			titles.remove(None)

		# return a list, sorted alphabetically
		self._titles = sorted(titles)
		return self._titles

	def _get_items_of_title(self, title):
		return LocationFilter(title).get_filtered_data(self.data)
