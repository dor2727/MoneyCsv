import os

from MoneyCsv.statistics import *
from MoneyCsv.utils import print_items, re_exact
from MoneyCsv.parsing import DataFolder, DataFile
from MoneyCsv.filters import initialize_time_filter, initialize_search_filter

# Find the relative file path (it may be a relative path)
def open_data_file(data_object=None, file_path=None):
	# this will mostly happen when called from the telegram bot,
	# 	which already uses a DataFolder
	if data_object:
		return data_object

	if not file_path:
		raise ValueError(f"file/folder not given")

	file_path = os.path.expanduser(file_path)

	if os.path.exists(file_path):
		if os.path.isfile(file_path):
			return DataFile(file_path)
		if os.path.isdir(file_path):
			return DataFolder(file_path)

	# try relative path:
	elif os.path.exists(rel_path := os.path.join(os.getcwd(), file_path)):
		if os.path.isfile(rel_path):
			return DataFile(rel_path)
		if os.path.isdir(rel_path):
			return DataFolder(rel_path)

	# try a path relative to the default directory:
	elif os.path.exists(rel_path := os.path.join(DEFAULT_DATA_DIRECTORY, file_path)):
		if os.path.isfile(rel_path):
			return DataFile(rel_path)
		if os.path.isdir(rel_path):
			return DataFolder(rel_path)

	raise ValueError(f"file/folder not found: {file_path}")

# use the filters & the data_object to filter out the relevant data
def get_data(data_object, args):
	# initialize filters
	time_filter   = initialize_time_filter(args)
	search_filter = initialize_search_filter(args)

	data = time_filter % data_object.data

	return data, time_filter, search_filter


# telegram helper - return the data in one of the following formats, according to args:
# 	pie, bar, telegram, text
def get_text(g, args):
	if args.telegram:
		if args.pie:
			return g.to_pie(save=True)
		elif args.bar:
			return g.to_bar(save=True)
		else:
			return g.to_telegram()

	else:
		if args.pie:
			g.to_pie(save=False)
			result = ''
		elif args.bar:
			g.to_bar(save=False)
			result = ''
		else:
			result = g.to_text()

		if args.show_items:
			result += "\n------\n"
			result += print_items(g.data, ret=True)

		return result


# handles the 'special' category of the args, or the default
def get_special_text(data, time_filter, args):
	detailedstats_params = {
		"time_filter"     : time_filter,
		"grouping_method" : args.grouping_method,
		"sorting_method"  : args.sorting_method,
	}
	kwargs = {}

	# big switch-case for different GroupedStats classes
	if args.friend:
		cls = DetailedStats_Friend
	elif args.location:
		cls = DetailedStats_Location

	elif args.group:
		cls = DetailedStats_Group
		kwargs = {
			"group_name": re_exact(args.group.lower()),
			# filter_obj_kwargs
			"case_sensitive": False,
			"regex": True,
		}

	else: # default statistics
		cls = DetailedStats_AllGroups


	g = cls(
		data,
		**kwargs,
		**detailedstats_params
	)

	return get_text(g, args)

# handles the 'extra-details' flag
def get_extra_details_text(data, time_filter, search_filter, args):
	detailedstats_params = {
		"time_filter"        : time_filter,
		"grouping_method"    : args.grouping_method,
		"sorting_method"     : args.sorting_method,
	}

	if args.extra_details_name is None:
		g = DetailedStats_ExtraDetail(
			search_filter,
			data,
			**detailedstats_params,
		)
	else:
		g = DetailedStats_ExtraDetailWithName(
			search_filter,
			args.extra_details_name,
			data,
			**detailedstats_params,
		)


	return get_text(g, args)

# handles search_filter
def get_search_filter_text(data, time_filter, search_filter, args):
	found_items = search_filter % data

	g = BasicStats(
		found_items,
		time_filter=time_filter
	)

	return get_text(g, args)
