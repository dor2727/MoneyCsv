import calendar
import datetime

from MoneyCsv.utils import get_midnight, format_dates
from MoneyCsv.filters.base_filters import Filter, TrueFilter

# do not use this class directly - it is a meta class
class BaseTimeFilter(Filter):
	def filter(self, data):
		return [
			i.is_in_date_range(self.start_time, self.stop_time)
			for i in data
		]

	def __str__(self):
		return format_dates(self.start_time, self.stop_time)

	def __repr__(self):
		name  = self.__class__.__name__
		start = self.start_time.strftime("%Y/%m/%d")
		stop  = self.stop_time.strftime("%Y/%m/%d")
		return f"{name}({start} --> {stop})"

	@property
	def _selected_time(self):
		raise NotImplemented

	@property
	def total_time(self):
		return (self.stop_time - self.start_time).total_seconds()


# A dummy class for when no time filter is used
class TimeFilter_None(TrueFilter):
	def __str__(self):
		return "All time"

	def __repr__(self):
		return f"{self.__class__.__name__}(All time)"

	@property
	def _selected_time(self):
		return "All time"

	@property
	def total_time(self):
		return float("inf")


class TimeFilter_Days(BaseTimeFilter):
	def __init__(self, days: int=7):
		"""
			amount of days to take
				1 means today only
				2 means today + yesterday
				8 means a week plus a day. E.g. from sunday to sunday, inclusive
		"""
		self.days = days

		self.stop_time = datetime.datetime.now()
		self.start_time = get_midnight(
			self.stop_time
			 -
			# added the "minus 1" since taking today only means taking midnight of now
			# thus, we need to reduce a timedelta of 0 days when amount of days is 1
			datetime.timedelta(days=days-1)
		)

	def __repr__(self):
		return f"{self.__class__.__name__}({self.days})"

	@property
	def _selected_time(self):
		return f"days ({self.days})"

class TimeFilter_Today(TimeFilter_Days):
	def __init__(self):
		super().__init__(days=1)
	def __repr__(self):
		return f"{self.__class__.__name__}"
class TimeFilter_ThisWeek(TimeFilter_Days):
	def __init__(self):
		super().__init__(days=7)
	def __repr__(self):
		return f"{self.__class__.__name__}"
class TimeFilter_Weeks(TimeFilter_Days):
	def __init__(self, weeks: int=7):
		"""
			amount of weeks to take
				1 means the past 7 days, including today
		"""
		self.weeks = weeks
		super().__init__(days=weeks*7)

	def __repr__(self):
		return f"{self.__class__.__name__}({self.weeks})"

	@property
	def _selected_time(self):
		return f"weeks ({self.weeks})"


class TimeFilter_Month(BaseTimeFilter):
	def __init__(self, month: int=0, year: int=0):
		"""
			if year==0: get the last occurence of that month
			else: get that specific month

			if month==0: get current month
		"""
		now = datetime.datetime.now()

		self.month = month or now.month

		if year == 0:
			if self.month > now.month:
				self.year = now.year - 1
			else:
				self.year = now.year
		else:
			self.year = year

		self.start_time = datetime.datetime(self.year, self.month, 1)
		self.stop_time  = datetime.datetime(self.year, self.month,
			calendar.monthrange(self.year, self.month)[1])

	def filter(self, data):
		return [
			i.date.year == self.year
			 and
			i.date.month == self.month
			for i in data
		]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.year}/{self.month})"

	@property
	def _selected_time(self):
		return f"month ({self.year}/{self.month})"

class TimeFilter_Year(BaseTimeFilter):
	def __init__(self, year: int=0):
		self.year = year or datetime.datetime.now().year

		self.start_time = datetime.datetime(self.year, 1,  1 )
		self.stop_time  = datetime.datetime(self.year, 12, 31)

	def filter(self, data):
		return [
			i.date.year == self.year
			for i in data
		]

	def __repr__(self):
		return f"{self.__class__.__name__}({self.year})"

	@property
	def _selected_time(self):
		return f"year ({self.year})"

class TimeFilter_DateRange(BaseTimeFilter):
	def __init__(self, start_time, stop_time,
		include_by_start=True, include_by_stop=False):
		"""
		date is included if:
			The whole Data object               is contained within the date_range
			include_by_start && Data.start_time is contained within the date_range
			include_by_stop  && Data.stop_time  is contained within the date_range
		"""

		self.start_time       = start_time
		self.stop_time        = stop_time
		self.include_by_start = include_by_start
		self.include_by_stop  = include_by_stop

	def filter(self, data):
		return [
			i.is_in_date_range(self.start_time, self.stop_time,
				self.include_by_start, self.include_by_stop)
			for i in data
		]

	@property
	def _selected_time(self):
		return "daterange"
