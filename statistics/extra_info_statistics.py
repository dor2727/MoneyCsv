from MoneyCsv.statistics.base_statistics import DetailedStats
from MoneyCsv.filters import GroupFilter, FriendFilter, LocationFilter

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
		return GroupFilter(title).get_filtered_data(self.data)

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
