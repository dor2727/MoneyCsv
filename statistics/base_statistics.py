import json
import math
import functools
import numpy as np
import matplotlib.pyplot as plt

from MoneyCsv.utils import shorten_selected_time, format_dates
from MoneyCsv.filters import SalaryFilter
from MoneyCsv.parsing.consts import CURRENCY_SYMBOL_NIS

# This is the only class with a different naming
# 	What's usually 'amount', is here named 'money'
class Stats(object):
	def __init__(self, data, time_filter=None):
		self.data = data
		self._time_filter = time_filter


	#
	# Exposing different properties of the data
	#
	@property
	def amount_of_transactions(self):
		return len(self.data)

	@property
	def amount_of_money(self):
		return sum(~SalaryFilter % self.data)

	@property
	def amount_of_salary(self):
		return sum( SalaryFilter % self.data)

	@property
	def amount_of_days(self):
		if self.data:
			dates = [i.date for i in self.data]
			return (max(dates) - min(dates)).days + 1
		else:
			return 0

	@property
	def transactions_per_day(self):
		if self.amount_of_days == 0:
			return 0

		return self.amount_of_transactions / self.amount_of_days

	@property
	def money_per_day(self):
		if self.amount_of_days == 0:
			return 0

		return self.amount_of_money / self.amount_of_days

	@property
	def average_money_per_transaction(self):
		if self.amount_of_transactions == 0:
			return 0

		return self.amount_of_money / self.amount_of_transactions


	#
	# Exposing different ways of printing the data
	#
	def __repr__(self):
		return self.__class__.__name__

	@property
	def selected_time(self):
		if self._time_filter is None:
			return "All time"

		return self._time_filter.selected_time

	@property
	def date_representation(self):
		if self.data:
			return format_dates(self.data[0].date, self.data[-1].date)
		else:
			return "no days found"

	@property
	def time_representation_str(self):
		return "%s [%s] (found %d days)" % (
			shorten_selected_time(self.selected_time),
			self.date_representation,
			self.amount_of_days
		)


	#
	# Exporing the data
	#
	def to_text(self):
		raise NotImplemented()

	def to_telegram(self):
		return self.to_text()

	def to_dict(self):
		raise NotImplemented()

	def to_csv(self):
		items = self.to_dict().items()
		# sort by keys
		items = sorted(items, key=lambda x: x[0])

		headers = [i[0] for i in items]
		values = [i[1] for i in items]
		return ','.join(headers) + '\n' + ','.join(values)

	def to_json(self):
		return json.dumps(self.to_dict(), sort_keys=True)

	def to_pie(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the pie chard
		if save is str: save the image to that path
		if save is True: save to the default location
		"""
		raise NotImplemented()

	def to_bar(self, headers=None, values=None, title=None, save=True):
		"""
		if bool(save) is False: interactively show the bar graph
		if save is str: save the image to that path
		if save is True: save to the default location
		"""
		raise NotImplemented()


class BasicStats(Stats):
	def to_text(self):
		s  = self.time_representation_str

		s += "\n"
		s += f"  transactions per day = {self.transactions_per_day:.2f}"
		s += " ; "
		s += f"  money per day = {self.money_per_day:.2f}"

		s += "\n"
		s += "    (%3d) : %.2f%s ; transaction average %.2f%s" % (
			self.amount_of_transactions,
			self.amount_of_money,
			CURRENCY_SYMBOL_NIS,
			self.average_money_per_transaction,
			CURRENCY_SYMBOL_NIS,
		)

		return s


def require_processed_data(func):
	@functools.wraps(func)
	def inner(self, *args, **kwargs):
		if not (hasattr(self, "titles_sorted") and hasattr(self, "values_sorted")):
			self.process_data()
		return func(self, *args, **kwargs)
	return inner

class DetailedStats(Stats):
	_allowed_grouping_methods = ("amount", "amount_average", "transactions")
	_allowed_sorting_methods  = ("alphabetically", "by_value")

	def __init__(self, data, time_filter=None, grouping_method="time", sorting_method="by_value"):
		super().__init__(data, time_filter)


		self._grouping_method = grouping_method.lower()
		if self._grouping_method not in self._allowed_grouping_methods:
			raise ValueError(f"invalid grouping_method: {grouping_method}")

		self._sorting_method = sorting_method.lower()
		if self._sorting_method not in self._allowed_sorting_methods:
			raise ValueError(f"invalid sorting_method: {sorting_method}")


	#
	# Required functions
	#
	def _get_titles(self):
		raise NotImplemented

	def _get_items_of_title(self, title):
		raise NotImplemented


	#
	# Process & sort titles & values
	#
	def process_data(self):
		"""
		processes self.data
		return 2 lists
			1) titles: each item is the name of the group
			2) values: each item is a list with the items
		"""
		titles = self._titles = self._get_titles()

		values = self._values = list(map(
			self._get_data_of_title,
			titles
		))

		self.titles_sorted, self.values_sorted = self._sort(titles, values)
		return self.titles_sorted, self.values_sorted

	def _sort(self, titles, values, exclude_salary=True):
		# if either headers or values are empty
		if not titles or not values:
			return titles, values

		z = zip(titles, values)

		# sort by title (str), alphabetically
		if self._sorting_method == "alphabetically":
			sorted_z = sorted(z, key=lambda i: i[0])
		# sort by value, highest first
		elif self._sorting_method == "by_value":
			sorted_z = sorted(z, key=lambda i: abs(i[1]), reverse=True)
		else:
			raise ValueError("invalid sorting_method")

		# unpack the zip into titles and values
		t, v = tuple(zip(*sorted_z))

		if exclude_salary and "Salary" in t:
			index = t.index("Salary")
			t = t[:index] + t[index+1:]
			v = v[:index] + v[index+1:]

		return t, v

	def _get_all_data_of_title(self, title):
		items = self._get_items_of_title(title)

		amount_of_transactions = len(items)
		amount_of_money = sum(items)

		if amount_of_transactions:
			average_money_per_transaction = amount_of_money / amount_of_transactions
		else:
			average_money_per_transaction = 0

		return amount_of_transactions, amount_of_money, average_money_per_transaction

	def _get_data_of_title(self, title):
		amount_of_transactions, amount_of_money, average_money_per_transaction = self._get_all_data_of_title(title)

		if self._grouping_method == "amount":
			return amount_of_money
		elif self._grouping_method == "transactions":
			return amount_of_transactions
		elif self._grouping_method == "amount_average":
			return average_money_per_transaction
		else:
			raise ValueError(f"invalid grouping_method: {self._grouping_method}")

	#
	# Plot utils
	#
	@property
	def title(self):
		return getattr(
			self,
			"_title",
			(
				f"{getattr(self, '_title_prefix', '')}"
				f"{self.__class__.__name__}"
				f"({self._grouping_method})"
				 " - "
				f"{self.selected_time}"
			)
		)

	@title.setter
	def title(self, value):
		self._title = value

	def _plot_save(self, fig, save):
		if save:
			if save is True:
				path = DEFAULT_PIE_PATH
			else:
				path = save

			fig.savefig(path)
			plt.close(fig)

			return open(path, "rb")

		# plotting - interactive
		else:
			plt.show()
			return None

	def _plot_set_title(self, fig, ax):
		ax.set_title(self.title)
		fig.canvas.manager.set_window_title(self.title)
		# fig.canvas.set_window_title(self.title)

	def _plot_make_pie(self, ax, values, titles):
		def pct(value):
			# value is given as a percentage - a float between 0 to 100
			amount_of_money = value * self.amount_of_money / 100
			return f"{value:.1f}%\n{amount_of_money}{CURRENCY_SYMBOL_NIS}"

		# making the pie chart
		patches, _, _ = ax.pie(values, labels=titles, autopct=pct)
		ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

		return patches

	def _plot_make_bar(self, ax, values, titles):
		# making the bar graph
		x = np.arange(len(titles))  # the label locations
		width = 0.35  # the width of the bars
		rects = ax.bar(x, values, width)

		# titles & labels
		ax.set_ylabel(self._grouping_method)
		ax.set_xticks(x)
		ax.set_xticklabels(titles)

		return rects

	#
	# Plotting
	#
	@require_processed_data
	def to_pie(self, save=True):
		"""
		if save:
			return open handle to the file with the image

			if save is str:
				save the image to that path
			if save is True:
				save to the default location

		if bool(save) is False:
			interactively show the pie chard
		"""
		# plotting initialization
		fig, ax = plt.subplots()

		patches = self._plot_make_pie(ax, self.values_sorted, self.titles_sorted)

		if hasattr(self, "_plot_make_pie_clickable"):
			self._plot_make_pie_clickable(fig, patches)

		self._plot_set_title(fig, ax)

		return self._plot_save(fig, save)

	@require_processed_data
	def to_bar(self, save=True):
		"""
		if save:
			return open handle to the file with the image

			if save is str:
				save the image to that path
			if save is True:
				save to the default location

		if bool(save) is False:
			interactively show the pie chard
		"""
		# plotting initialization
		fig, ax = plt.subplots()

		self._plot_make_bar(ax, self.values_sorted, self.titles_sorted)

		self._plot_set_title(fig, ax)

		return self._plot_save(fig, save)


	#
	# Text utils
	#
	def _generate_text(self, header, text_per_item, footer):
		s  = header()

		for t in self.titles_sorted:
			s += "\n"
			s += text_per_item(t)

		if "Salary" in self._titles:
			s += "\n"
			s += "    " + '-'*50
			s += "\n"
			s += text_per_item("Salary")

		s += "\n"
		s += footer()

		return s

	@property
	def _text_title_format(self):
		return "%%-%ds" % (max(map(len, self.titles_sorted), default=1) + 1)

	@property
	def _money_str_format(self):
		# 4 stands for ['-', '.', 2 digits after the dot, 'nis']
		return "%%%d.2f" % (math.ceil(math.log10(max(map(abs, self.data)))) + 4)

	def _text_generate_header(self):
		s  = self.time_representation_str
		s += "\n"
		s += f"  transactions per day = {self.transactions_per_day:.2f}"
		s += " ; "
		s += f"  money per day = {self.money_per_day:.2f}"
		return s

	def _text_generate_footer(self):
		if not self.titles_sorted:
			return "    No titles found :("
		if not self.amount_of_transactions:
			return "    No transactions found :("

		s  = "    " + '-'*50
		s += "\n"
		s += "    %s (%4d) : %.2f" % (
			(self._text_title_format % "Total"),
			self.amount_of_transactions,
			self.amount_of_money,
		)

		if "Salary" in self._titles:
			s += " -> "
			# Salary is positive, amount_of_money is negative
			s += "Net total %.2f" % (self.amount_of_salary + self.amount_of_money)
		return s

	def _text_generate_item(self, title):
		amount_of_transactions, amount_of_money, average_money_per_transaction = self._get_all_data_of_title(title)

		money_percentage = abs(amount_of_money / self.amount_of_money * 100.0)

		return "    %s (%4d) : %s (%5.2f%%) ; item average %s" % (
			(self._text_title_format % title),
			amount_of_transactions,
			(self._money_str_format % amount_of_money),
			money_percentage,
			(self._money_str_format % average_money_per_transaction),
		)

	def _telegram_generate_item(self, title):
		amount_of_transactions, amount_of_money, average_money_per_transaction = self._get_all_data_of_title(title)

		money_percentage = amount_of_money / self.amount_of_money * 100.0

		return "    %s\n        (%4d) : %s (%5.2f%%)" % (
			(self._text_title_format % title),
			amount_of_transactions,
			(self._money_str_format % amount_of_money),
			money_percentage,
		)

	#
	# Printing
	#
	@require_processed_data
	def to_text(self):
		return self._generate_text(
			self._text_generate_header,
			self._text_generate_item,
			self._text_generate_footer,
		)

	@require_processed_data
	def to_telegram(self):
		return self._generate_text(
			self._text_generate_header,
			self._telegram_generate_item,
			self._text_generate_footer,
		)


class DetailedStatsFiltered(DetailedStats):
	def __init__(self, data, filter_obj, time_filter=None, grouping_method="time", sorting_method="by_value"):
		super().__init__(data, time_filter, grouping_method, sorting_method)

		self._filter_obj = filter_obj

		self._initialize_data()

	def _initialize_data(self):
		self._original_data = self.data
		self.data = self._filter_obj % self.data
