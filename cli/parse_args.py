import sys
import argparse

from MoneyCsv.consts import DEFAULT_DATA_DIRECTORY

try:
	from MoneyCsv.tests import test
except ImportError:
	def test(*args, **kwargs):
		print("no `tests` file found")

# may pass arguments as a list (used in the telegram bot)
def parse_args(args_list=None):
	parser = argparse.ArgumentParser()
	parser.add_argument("--file", "--folder", "-f", type=str, default=DEFAULT_DATA_DIRECTORY, dest="file", help="which file/folder to read")

	search = parser.add_argument_group("Search")
	search.add_argument("search_string"        , type=str, default=''        , nargs=argparse.REMAINDER)
	search.add_argument("--group-by"           , type=str, default="amount"  , dest="grouping_method", help="grouping method (amount or amount_average/avg or transactions)")
	
	search.add_argument("--sort"               , type=str, default="by_value", dest="sorting_method" , help="sorting method (by_value/value or alphabetically/abc)")
	search.add_argument("--abc"                , action="store_true"         , dest="sorting_abc"    , help="short for '--sort alphabetically")
	search_advanced = parser.add_argument_group("Advanced search")
	search_advanced.add_argument("--search-use-or"      , action="store_true"         , dest="search_use_or"  , help="whether to use AND or OR when adding the filters. Default: AND")
	search_advanced.add_argument("--show-items", "-s"   , action="store_true"         , dest="show_items"     , help="whether to print all the items")
	search_advanced.add_argument("--force-regex", "--re", action="store_true"         , dest="force_regex"    , help="whether to use regex in all search terms")

	time = parser.add_argument_group("Time")
	time.add_argument("--days-back", "-d", type=int , default=None, dest="days_back"   , help="how many days back to query")
	time.add_argument("--months-back"    , type=int , default=None, dest="months_back" , help="how many month summaries to show")
	time.add_argument("--month"    , "-m", type=str , default=None, dest="month"       , help="which month to query. can be comma seperated (e.g. 1,2,3,9)")
	time.add_argument("--year"     , "-y", type=str , default=None, dest="year"        , help="which year to query. can be comma seperated (e.g. 2019,2020)")
	time.add_argument("--all-time"       , action="store_true"    , dest="all_time"    , help="whether to all the time")
	time.add_argument("--time-use-and"   , action="store_true"    , dest="time_use_and", help="whether to use AND or OR when adding the filters")


	debugging = parser.add_argument_group("Debugging")
	debugging.add_argument("--debug", action="store_true")
	debugging.add_argument("--test" , action="store_true")
	debugging.add_argument("--pdb"  , action="store_true")

	grouping = parser.add_argument_group("grouping")
	grouping.add_argument("--all-groups", "--all", action="store_true"    , dest="all_groups"  , help="show statistics of all groups")
	grouping.add_argument("--group"              , type=str , default=None, dest="group"       , help="show statistics per group")
	grouping.add_argument("--friend", "--friends", action="store_true"    , dest="friend"      , help="show friend statistics")
	grouping.add_argument("--location"           , action="store_true"    , dest="location"    , help="show location statistics")
	#
	grouping.add_argument("--food"               , action="store_true"    , dest="food"        , help="show food statistics")

	details = parser.add_argument_group("details")
	details.add_argument("--extra-details", "--extra", action="store_true",     dest="extra_details"     , help="extra details within the search filter")
	details.add_argument("--extra-details-name"      , type=str , default=None, dest="extra_details_name", help="sets the name of the extra details. Useful for cases when multiple names are found")

	output = parser.add_argument_group("output")
	output.add_argument("--telegram", action="store_true")
	output.add_argument("--pie"     , action="store_true")
	output.add_argument("--bar"     , action="store_true")


	if args_list is None:
		args = parser.parse_args()
	else:
		args = parser.parse_args(args_list)

	return post_process_args(args)

def expand_args(args):
	if args.sorting_method == "abc":
		args.sorting_method = "alphabetically"
	if args.sorting_method == "value":
		args.sorting_method = "by_value"
	if args.sorting_abc:
		args.sorting_method = "alphabetically"

	if args.grouping_method == "avg":
		args.grouping_method = "amount_average"

	if args.food:
		args.group = "Food"

	if args.extra_details:
		args.force_regex = True

def post_process_args(args):
	if args.debug:
		print(f"[*] args: {args}")

	expand_args(args)


	if args.pdb:
		import ipdb; ipdb.set_trace()


	if args.test:
		test(debug=args.debug)
		sys.exit()


	return args
