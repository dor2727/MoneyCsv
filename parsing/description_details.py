import re

from MoneyCsv.utils import ordered_unique
from MoneyCsv.parsing.consts import *

class DescriptionDetailsParser(object):
	PATTERN_STRIP = None
	PATTERN_EXTRACT = None

	# this function requires the whole DataItem object
	@classmethod
	def extract_values(self, dataitem):
		raise NotImplemented

	# this function requires only the description
	@classmethod
	def strip(self, string):
		return re.sub(self.PATTERN_STRIP, '', string).strip()


class DescriptionDetailsParser_ExtraDetails(DescriptionDetailsParser):
	PATTERN_STRIP   = EXTRA_DETAILS_PATTERN_STRIP
	PATTERN_EXTRACT = EXTRA_DETAILS_PATTERN_EXTRACT

	@classmethod
	def extract_values(self, dataitem):
		try:
			extra_details = re.findall(self.PATTERN_EXTRACT, dataitem.description)
		except:
			import ipdb; ipdb.set_trace()

		extra_details_dict = {
			k: v.split(EXTRA_DETAILS_SEPERATOR)
			for k,v in extra_details
		}

		return extra_details_dict

class DescriptionDetailsParser_Friends(DescriptionDetailsParser):
	PATTERN_STRIP   = FRIEND_PATTERN_STRIP + [FRIEND_PATTERN_TO_FRIENDS]
	PATTERN_EXTRACT = FRIEND_PATTERN_EXTRACT

	@classmethod
	def extract_values(self, dataitem):
		found = self._get_all_friends(self, dataitem)

		friends_list = self._combine_friends_list(self, found)

		# unique
		return ordered_unique(friends_list)

	def _get_all_friends(self, dataitem):
		found = []
		for pattern in self.PATTERN_EXTRACT:
			found += re.findall(pattern, dataitem.description)

		# search_at_beginning 
		if dataitem.group == "Friends":
			found += re.findall(f"^{PATTERN_NAMES_LIST}", dataitem.description)

		return found

	def _combine_friends_list(self, friends_list):
		# join all results into a big string
		friends_list = ' '.join(i[0] for i in friends_list)
		# remove 'and', and convert back into a list
		friends_list = re.sub("\\band\\b", '', friends_list)
		friends_list = friends_list.split()
		return friends_list

	@classmethod
	def strip(self, string):
		for pattern in self.PATTERN_STRIP:
			string = re.sub(pattern, '', string)
		return string.strip()

	# An extracted API for finding friends in a string without a dataitem
	@classmethod
	def extract_values_from_string(self, string):
		found = []
		for pattern in self.PATTERN_EXTRACT:
			found += re.findall(pattern, string)

		friends_list = self._combine_friends_list(self, found)

		# unique
		return ordered_unique(friends_list)

class DescriptionDetailsParser_Location(DescriptionDetailsParser):
	PATTERN_STRIP   = PATTERN_LOCATION
	PATTERN_EXTRACT = PATTERN_LOCATION


	@classmethod
	def extract_values(self, dataitem):
		return self.extract_values_from_string(dataitem.description)

	@classmethod
	def strip(self, string):
		string = re.sub(self.PATTERN_STRIP, '', string)
		string = re.sub(PATTERN_LOCATION_THEIR_PLACE, '', string)
		return string.strip()

	# An extracted API for finding a location in a string without a dataitem
	@classmethod
	def extract_values_from_string(self, string):
		if PATTERN_LOCATION_THEIR_PLACE in string:
			return "Their place"

		l = re.findall(self.PATTERN_EXTRACT, string)
		if len(l) == 0:
			return None
		elif len(l) == 1:
			return l[0]
		else:
			print(f"[!] Multiple locations found: {l}")
			raise ValueError(f"Too many ({len(names)}) possible locations found")


DETAIL_PARSERS = {
	"extra_details": DescriptionDetailsParser_ExtraDetails,
	"friends"      : DescriptionDetailsParser_Friends,
	"location"     : DescriptionDetailsParser_Location,
}
