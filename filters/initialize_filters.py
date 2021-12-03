import datetime

from MoneyCsv.consts import DEFAULT_DATA_DIRECTORY
from MoneyCsv.filters.generic_filters import AutoFilter
from MoneyCsv.filters.time_filters    import TimeFilter_None    , \
											 TimeFilter_Days    , \
											 TimeFilter_Month   , \
											 TimeFilter_Year
from MoneyCsv.filters.filter_utils import 	 join_filters_with_or, \
											 join_filters_with_and

def initialize_search_filter(args):
	filters = [
		AutoFilter(s, force_regex=args.force_regex)
		for s in args.search_string
	]

	if not filters:
		f = None
	elif args.search_use_or:
		f = join_filters_with_or(filters)
	else:
		f = join_filters_with_and(filters)

	if args.debug:
		print(f"[*] search filter: {f}")

	return f

def initialize_time_filter(args):
	if args.all_time:
		return TimeFilter_None()

	time_filter   = build_time_filter(args)

	# if nothing is set, use default value
	if time_filter is None:
		# if the default location is used, set the filter to 2 months
		if args.file == DEFAULT_DATA_DIRECTORY:
			args.months_back = 2
			time_filter = build_time_filter(args)
		# else, treat it as `all_time`
		else:
			time_filter = TimeFilter_None()

	return time_filter

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


	if not filters:
		f = None
	elif args.time_use_and:
		f = join_filters_with_and(filters)
	else:
		f = join_filters_with_or(filters)

	if args.debug:
		print(f"[*] time filter: {f}")

	return f
