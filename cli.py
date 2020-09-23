#!/usr/bin/rlwrap python3

import os
import sys
import argparse
import datetime

import MoneyCsv.statistics
from MoneyCsv.parsing import DataFile, DataFileList, DataItem_with_discount
from MoneyCsv.money_utils import newest
from MoneyCsv.filters import *
from MoneyCsv.filters_special import *



# may pass arguments as a list (used in the telegram bot)
def parse_args(args_list=None):
	parser = argparse.ArgumentParser()

	search = parser.add_argument_group("search")
	search.add_argument("search_string"     , type=str, default=''        , nargs=argparse.REMAINDER)
	search.add_argument("--group-by"        , type=str, default="money"   , dest="grouping_method", help="grouping method (money or money_average/avg or transactions)")
	search.add_argument("--sort"            , type=str, default="by_value", dest="sorting_method" , help="sorting method (by_value/value or alphabetically/abc)")
	search.add_argument("--search-use-or"   , action="store_true"         , dest="search_use_or"  , help="whether to use AND (default) or OR when adding the filters")
	search.add_argument("--show-items", "-s", action="store_true"         , dest="show_items"     , help="whether to print all the items")

	time = parser.add_argument_group("time")
	time.add_argument("--days-back", "-d", type=int , default=None, dest="days_back"   , help="how many days back to query")
	time.add_argument("--months-back"    , type=int , default=None, dest="months_back" , help="how many month summaries to show")
	time.add_argument("--month"    , "-m", type=str , default=None, dest="month"       , help="which month to query. can be comma seperated (e.g. 1,2,3,9)")
	time.add_argument("--year"     , "-y", type=str , default=None, dest="year"        , help="which year to query. can be comma seperated (e.g. 2019,2020)")
	time.add_argument("--all-time"       , action="store_true"    , dest="all_time"    , help="whether to all the time")
	time.add_argument("--time-use-and"   , action="store_true"    , dest="time_use_and", help="whether to use AND or OR (default) when adding the filters")


	debugging = parser.add_argument_group("debugging")
	debugging.add_argument("--debug"   , action="store_true")
	debugging.add_argument("--test"    , action="store_true")
	debugging.add_argument("--telegram", action="store_true")

	special = parser.add_argument_group("special")
	special.add_argument("--subject"              , type=str , default=None, dest="subject"   , help="show statistics per subject")
	special.add_argument("--gaming"               , action="store_true"    , dest="gaming"    , help="show gaming statistics")
	special.add_argument("--friend", "--friends"  , action="store_true"    , dest="friend"    , help="show friend statistics")
	special.add_argument("--location"             , action="store_true"    , dest="location"  , help="show location statistics")
	special.add_argument("--shopping"             , action="store_true"    , dest="shopping"  , help="show shopping statistics")
	special.add_argument("--food"                 , action="store_true"    , dest="food"      , help="show food statistics")
	special.add_argument("--self-gifts"           , action="store_true"    , dest="self_gifts", help="show self gifts statistics")

	if args_list is None:
		args = parser.parse_args()
	else:
		args = parser.parse_args(args_list)

	if args.debug:
		print(f"[*] args: {args}")

	return args

#
# time filters
#
def build_time_filter(args):
	filters = []

	if args.days_back is not None:
		filters.append(TimeFilter_Days(args.days_back))

	if args.month is not None:
		month_filters = [
			TimeFilter_Month(int(m))
			for m in args.month.split(',')
		]
		filters.append(join_filters_with_or(month_filters))

	if args.year is not None:
		year_filters = [
			TimeFilter_Year(int(y))
			for y in args.year.split(',')
		]
		filters.append(join_filters_with_or(year_filters))
		
	if args.months_back is not None:
		current_month = datetime.datetime.now().month

		months_back_filters = []

		for i in range(args.months_back):
			m = ((current_month - 1 - i)  % 12) + 1
			months_back_filters.append(TimeFilter_Month(int(m)))

		filters.append(join_filters_with_or(months_back_filters))


	if args.time_use_and:
		f = join_filters_with_and(filters)
	else:
		f = join_filters_with_or(filters)

	if args.debug:
		print(f"[*] time filter: {f}")

	return f

def initialize_time_filter(args):
	if args.all_time:
		return None

	time_filter   = build_time_filter(args)

	if time_filter is None:
		args.months_back = 2
		time_filter = build_time_filter(args)

	return time_filter

def initialize_search_filter(args):
	filters = []

	for s in args.search_string:
		filters.append(AutoFilter(s))

	if args.search_use_or:
		f = join_filters_with_or(filters)
	else:
		f = join_filters_with_and(filters)

	if args.debug:
		print(f"[*] search filter: {f}")

	return f

# use the filters & the DataFile to filter out the relevant data
def get_data(datafile, args):
	# initialize filters
	time_filter   = initialize_time_filter(args)
	search_filter = initialize_search_filter(args)

	
	# filter data by time
	if time_filter is None:
		data = datafile.data
		selected_time = "All time"
	else:
		data = time_filter % datafile.data
		selected_time = time_filter.get_selected_time()

	return data, selected_time, search_filter

# telegram helper
def get_text(g, args):
	if args.telegram:
		return g.to_telegram()
	else:
		return g.to_text()

# handles the 'special' category of the args, or the default
def get_special_text(data, selected_time, args):
	if args.sorting_method == "abc":
		args.sorting_method = "alphabetically"
	if args.sorting_method == "value":
		args.sorting_method = "by_value"

	if args.grouping_method == "avg":
		args.grouping_method = "money_average"


	groupedstats_params = {
		"selected_time" : selected_time,
		"group_value"   : args.grouping_method,
		"sort"          : args.sorting_method,
	}
	# big switch-case for different GroupedStats classes
	if args.gaming:
		g = MoneyCsv.statistics.GroupedStats_Games(
			data,
			**groupedstats_params
		)

	elif args.friend:
		g = MoneyCsv.statistics.GroupedStats_Friend(
			data,
			**groupedstats_params
		)

	elif args.location:
		g = MoneyCsv.statistics.GroupedStats_Location(
			data,
			**groupedstats_params
		)

	elif args.subject:
		g = MoneyCsv.statistics.SubjectGroupedStats(
			data,
			category_name=args.subject.capitalize(),
			**groupedstats_params
		)

	elif args.shopping:
		g = MoneyCsv.statistics.FilteredGroupedStats(
			data,
			filter_obj=filter_shopping,
			**groupedstats_params
		)

	elif args.food:
		g = MoneyCsv.statistics.FilteredGroupedStats(
			data,
			filter_obj=filter_food,
			**groupedstats_params
		)

	elif args.self_gifts:
		g = MoneyCsv.statistics.FilteredGroupedStats(
			data,
			filter_obj=filter_self_gifts,
			**groupedstats_params
		)

	else: # default statistics
		g = MoneyCsv.statistics.GroupedStats_Subject(
			data,
			**groupedstats_params
		)

	return get_text(g, args)

# handles search_filter
def get_search_filter_text(data, selected_time, search_filter, args):
	found_items = search_filter % data

	g = MoneyCsv.statistics.FilteredStats(
		found_items,
		selected_time=selected_time
	)
	result = get_text(g, args)

	if args.show_items:
		result += "\n------\n"
		result += print_items(found_items, ret=True)

	return result

def main(datafile, args_list=None):
	# datafile can also be DataFileList
	args = parse_args(args_list=args_list)

	if args.test:
		test(debug=args.debug)
		return

	data, selected_time, search_filter = get_data(datafile, args)

	if search_filter is None:
		return get_special_text(data, selected_time, args)
	else:
		return get_search_filter_text(data, selected_time, search_filter, args)

def test(debug=False):
	print("[*] test")

	# create all DataFiles
	visa = DataFile("Visa")
	cash = DataFile("cash")
	transactions = DataFile("Transactions")
	isracard = DataFile("isracard",
		data_item_class=DataItem_with_discount
	)

	# join them
	datafiles = DataFileList(visa, cash, transactions, isracard)

	data = visa.data

	if debug:
		print(f"DataFile: {visa}")
		print(f"DataFileList: {datafiles}")


	f = TimeFilter_Days(20) & AmountFilter(100)

	f_data = f.get_filtered_data(data)
	print(len(f_data))

	g = MoneyCsv.statistics.GroupedStats_Games(f_data, group_value="transactions")
	# g = MoneyCsv.statistics.GroupedStats_Location(f_data)
	# g = MoneyCsv.statistics.GroupedStats_Youtube(f_data, group_value="money")
	# g = MoneyCsv.statistics.SubjectGroupedStats(f_data, group_value="money", category_name="Aliexpress")
	print(g.group())
	print(g.to_text())
	print(g.to_bar())
	# print(g.to_pie(save=False))

	import pdb; pdb.set_trace()

