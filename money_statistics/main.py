#!/usr/bin/env python3
import os
import re
import csv
import sys
import utils
import calendar
import datetime

import plotters

# 01/01/01 is Monday
DAYS = [datetime.datetime(1,1,i).strftime("%a") for i in range(1,7+1)]
# headers to look for in every csv
BASE_HEADERS = ["Date", "Amount", "Subject", "Description"]
# how to format [from_day - to_day]
DATE_REPRESENTATION_PATTERN = "%04d/%02d/%02d - %04d/%02d/%02d"


# pattern_with = "(?<=with )(.*?)(?=\\s[@\\(]|$)"
# a name starts with a capital letter
#    I write full names without spaces
_cappital_word = "[A-Z][A-Za-z]*"
# names list is
#     Name Name Name and Name
#     which is - at least one
#         where the last one (if there is more than one) follows "and"
#         and any name which is not the first nor the last has space before and after itself
_names_list  = "((%s)( %s)*( and %s)*)" % (tuple([_cappital_word])*3)
pattern_with = re.compile("(?<=with )" + _names_list)
pattern_for  = re.compile("(?<=for )"  + _names_list)


class DataPlotter(object):
	def __init__(self, money, name):
		self._money = money
		self._name  = name

	def __call__(self, *args, **kwargs):
		return getattr(self._money, self._name) (*args, **kwargs)

class TypePlotter(object):
	def __init__(self, money, name):
		self._money = money
		self._name  = name

		self._group = getattr(self, "_group_data_by_" + name)

		self.friends = DataPlotter(self._money, self._name + '_' + "friends")
		self.weekday = DataPlotter(self._money, self._name + '_' + "weekday")
		self.title   = DataPlotter(self._money, self._name + '_' + "title")

		self.subject = self.title
	"""
	@abstractmethod
	def _group_data(self):
		pass
	"""

	@staticmethod
	def _group_data_by_title(data, titles, salary=None):
		"""
		data   - list of Data objects
		titles - list for strings of titles names
		salary - list of Data objects
		"""

		# create a hash-table linking title_name to its index in the titles list
		titles_index = {t:i for i,t in enumerate(titles)}
		# create 2 lists to sort the data for every title
		# I am using lists and not dictionaries since they are sorted
		transactions_per_title = [0]*len(titles)
		money_per_title        = [0]*len(titles)

		for d in data:
			transactions_per_title[titles_index[d.subject]] += 1
			money_per_title       [titles_index[d.subject]] += d.amount

		if salary is not None:
			for d in salary:
				transactions_per_title[titles_index[d.subject]] += 1
				money_per_title       [titles_index[d.subject]] += d.amount

		return transactions_per_title, money_per_title


class VisualPlotter(object):
	def __init__(self, money, name):
		self._money = money
		self._name  = name

		self.money        = TypePlotter(self._money, self._name + '_' + "money")
		self.transacrions = TypePlotter(self._money, self._name + '_' + "transacrions")
	"""
	@abstractmethod
	def _plot(self, headers, data, title):
		pass
	def _pre_plot(self, *args, **kwargs):
		pass
	def _post_plot(self, *args, **kwargs):
		pass
	"""

class Plotter(object):
	def __init__(self, money, name):
		self._money = money
		self._name  = name

		self.bar  = VisualPlotter(self._money, self._name + '_' + "bar")
		self.pie  = VisualPlotter(self._money, self._name + '_' + "pie")
		self.text = VisualPlotter(self._money, self._name + '_' + "text")
		self.top  = VisualPlotter(self._money, self._name + '_' + "top")


class Data(object):
	def __init__(self, items, headers, parsers):
		self._items = []
		for i in range(len(headers)):
			self._items.append(
				parsers[i](items[i])
			)

			setattr(
				self,
				headers[i].lower(),
				self._items[-1]
			)

	def __getitem__(self, n):
		return self._items[n]

	def __repr__(x):
		return "%s : %8.2f : %-10s : %s" % (
			x.date.strftime("%Y/%m/%d"),
			x.amount,
			x.subject,
			x.description
		)

	@property
	def friends(self):
		# get all from the patterns
		found = (
			pattern_with.findall(self.description)
			 +
			pattern_for .findall(self.description)
		)
		# join all results into one string
		found = ' '.join(i[0] for i in found)
		
		return found.replace("and", "").split()


class Money(object):
	def __init__(self, path=None):
		self.load_data(path or self.default_path)
		self.create_titles()
		self.create_friends_list()

		# self.plot = Plotter(self, "_plot")
		self.plot = plotters.Plot(get_data=self.get_data)
		
	def load_data(self, path):
		r = csv.reader(
			open(
				os.path.expandvars(
					os.path.expanduser(
						path
					)
				)
			)
			# open(path)
		)
		self.headers = next(r)
		# self.data = list(r)
		self.data = list(map(
			lambda x: Data(x, self.headers, self.PARSERS),
			r
		))

	def create_titles(self):
		self.titles = list(set(i.subject for i in self.data))

		self.titles_without_salary = self.titles[:]
		if "Salary" in self.titles_without_salary:
			self.titles_without_salary.remove("Salary")

	def create_friends_list(self):
		# pattern_with = "(?<=with )(.*?)(?=\\s[@\\(]|$)"
		# a name starts with a capital letter
		#    I write full names without spaces
		_cappital_word = "[A-Z][A-Za-z]*"
		# names list is
		#     Name Name Name and Name
		#     which is - at least one
		#         where the last one (if there is more than one) follows "and"
		#         and any name which is not the first nor the last has space before and after itself
		_names_list  = "((%s)( %s)*( and %s)*)" % (tuple([_cappital_word])*3)
		pattern_with = "(?<=with )" + _names_list
		pattern_for  = "(?<=for )"  + _names_list
		descriptions = '\n'.join(i.description for i in self.data)

		all_friends_raw = [i[0] for i in re.findall(pattern_with, descriptions)] \
						+ [i[0] for i in re.findall(pattern_for , descriptions)]
		self._friends_unsorted = '\n'.join(all_friends_raw).replace("and", "").split()

		self.friends_histogram = utils.counter(self._friends_unsorted)
		self.friends_histogram.sort(key=lambda x:-x[1])

		self.friends = [i[0] for i in self.friends_histogram]

	def get_data(self, year=None, month=None, bank_month=True):
		if not month:
			if not year:
				selected_time = "All times"
				# this is copied to another list, so self.data will not be changed
				items = list(self.data)
			else:
				selected_time = str(year)
				items = list(filter(
					lambda i: i.date.year == year,
					self.data
				))
				
			days_representation = DATE_REPRESENTATION_PATTERN % (
				items[ 0].date.year,
				items[ 0].date.month,
				items[ 0].date.day,
				items[-1].date.year,
				items[-1].date.month,
				items[-1].date.day,
			)
			amount_of_days = (items[-1].date - items[0].date).days
		else:
			amount_of_days = calendar.monthrange(year, month)[1]

			if bank_month:
				if month == 12:
					next_year  = year + 1
					next_month = 1
				else:
					next_year  = year
					next_month = month + 1
				limit_low  = datetime.datetime(     year,      month, 10)
				limit_high = datetime.datetime(next_year, next_month, 10)

				items = list(filter(
					lambda i: limit_low <= i.date < limit_high,
					self.data
				))
				days_representation = DATE_REPRESENTATION_PATTERN % (year, month, 10, next_year, next_month, 9)
			else:
				items = list(filter(
					lambda i: i.date.year == year and i.date.month == month,
					self.data
				))
				days_representation = DATE_REPRESENTATION_PATTERN % (year, month, 1, year, month, calendar.monthrange(year, month)[1])

			selected_time = items[0].date.strftime("%Y - %m (%B)")


		items_without_salary = list(filter( lambda x: x.subject != "Salary", items ))
		salary               = list(filter( lambda x: x.subject == "Salary", items ))

		# time_representation = "%-21s (%s) (%d days)" % (
		time_representation = "%s (%s) (%d days)" % (
			selected_time,
			days_representation,
			amount_of_days
		)

		return items_without_salary, salary, time_representation, amount_of_days

	def _plot_bar_money_title(self, year=None, month=None, bank_month=True, include_salary=False):
		items, salary, time_representation, amount_of_days = self.get_data(year, month, bank_month)

		transactions_per_title, money_per_title = TypePlotter._group_data_by_title(
			items,
			self.titles_without_salary if include_salary else self.titles,
			salary=salary              if include_salary else None
		)

		utils.plot.bar(
			money_per_title, # data
			self.titles if include_salary else self.titles_without_salary, # names
			title="Money per Subject"
		)
	def _plot_pie_money_title(self, year=None, month=None, bank_month=True, include_salary=False):
		items, salary, time_representation, amount_of_days = self.get_data(year, month, bank_month)

		transactions_per_title, money_per_title = TypePlotter._group_data_by_title(
			items,
			self.titles_without_salary if include_salary else self.titles,
			salary=salary              if include_salary else None
		)
		
		utils.plot.pie(
			money_per_title, # data
			self.titles if include_salary else self.titles_without_salary, # names
			title="Money per Subject"
		)
	def _plot_text_money_title(self, year=None, month=None, bank_month=True, include_salary=False):
		items, salary, time_representation, amount_of_days = self.get_data(year, month, bank_month)
		total = sum(i[1] for i in items)

		transactions_per_title, money_per_title = TypePlotter._group_data_by_title(
			items,
			self.titles_without_salary if include_salary else self.titles,
			salary=salary              if include_salary else None
		)
		
		print(time_representation)

		# print basic statistics
		print("  items per day = %.2f" % (len(items)     / amount_of_days))
		print("  days per item = %.2f" % (amount_of_days / len(items)    ))
		print("  avg per day   = %.2f" % (total          / amount_of_days))
		print("  avg per item  = %.2f" % (total          / len(items)    ))

		titles = self.titles if include_salary else self.titles_without_salary
		titles_index = {t:i for i,t in enumerate(titles)}

		for t in titles:
			print("    %-10s (%2d) : %7.1f (%02d%%)" % (
				t,
				transactions_per_title[titles_index[t]],
				money_per_title       [titles_index[t]],
				money_per_title       [titles_index[t]] / total * 100
			))

		print("    " + '-'*29)
		print("    %-10s (%2d) : %7.1f [%5d]" % (
			"Total",
			len(items),
			total,
			sum(i.amount for i in salary)
		))
		print()
	def _plot_top_money_title(self, year=None, month=None, bank_month=True, include_salary=False, n=5):
		items, salary, time_representation, amount_of_days = self.get_data(year, month, bank_month)

		transactions_per_title, money_per_title = TypePlotter._group_data_by_title(
			items,
			self.titles_without_salary if include_salary else self.titles,
			salary=salary              if include_salary else None
		)
		
		print(time_representation)

		items.sort(key=lambda x: x[self.headers.index("Amount")])

		for i in range(n):
			print(repr(items[i]))
		print()

	def _plot_bar_money_friend(self, year=None, month=None, bank_month=True, include_salary=True, amount=5):
		pass
	def _plot_pie_money_friend(self, year=None, month=None, bank_month=True, include_salary=True, amount=5):
		pass
	def _plot_text_money_friend(self, year=None, month=None, bank_month=True, include_salary=True, amount=5):
		pass
	
	def _plot_bar_money_weekday(self, year=None, month=None, bank_month=True, include_salary=True):
		pass
	def _plot_pie_money_weekday(self, year=None, month=None, bank_month=True, include_salary=True):
		pass
	def _plot_text_money_weekday(self, year=None, month=None, bank_month=True, include_salary=True):
		### verify
		# if bank_month - get previous month's amount of days
		items, salary, time_representation, amount_of_days = self.get_data(year, month, bank_month)
		total = sum(i[1] for i in items)

		print(time_representation)

		# every day, starting at Sunday, where Monday == 0
		for day in [6] + list(range(0,6)):
			day_items = list(filter(
				lambda x: x[0].weekday() == day,
				items
			))

			print("    %-3s (%2d) : %7.1f (%02d%%)" % (
				DAYS[day],
				len(day_items),
				sum(i[1] for i in day_items),
				sum(i[1] for i in day_items) / total * 100
			))

		print("  " + '-'*26)
		print("  Total (%2d) : %7.1f [%5d]" % (
			len(items),
			total,
			sum(i[1] for i in salary)
		))
		print()

	def stats(self, amount):
		# get month list
		months = list(set((i[0].year, i[0].month) for i in self.data))
		months.sort(key=lambda x: x[0]*12 + x[1], reverse=True)
		if amount:
			months = months[:amount]

		for m in months:
			amount_of_days = calendar.monthrange(*m)[1]
			# get each month's items
			items = [i for i in self.data if i[0].year == m[0] and i[0].month == m[1]]

			month_total = sum(i[1] for i in items)

			# print month's title
			print(items[0][0].strftime("%Y - %m (%B)"))

			# print basic statistics
			print("  items per day = %.2f" % (len(items) / amount_of_days))
			print("  days per item = %.2f" % (amount_of_days / len(items)))
			print("  avg per day   = %.2f" % (month_total / amount_of_days))
			print("  avg per item  = %.2f" % (month_total / len(items)))

			for t in self.titles:
				print("    %-10s (%2d) : %8.2f (%02d%%)" % (
					t,
					len(list(filter(
						lambda x: x[2] == t,
						items
					))),
					sum(i[1] for i in items if i[2] == t),
					sum(i[1] for i in items if i[2] == t) / month_total * 100
				))

			print("    " + '-'*29)
			print("    %-10s (%2d) : %8.2f [%5d]" % (
				"Total",
				len(items),
				month_total,
				827 - month_total
			))
			print()

class Visa(Money):
	PARSERS = [
		lambda x: datetime.datetime.strptime(x, "%Y/%m/%d"),
		float,
		str,
		str
	]
	default_path = "~/Projects/Money/visa.csv"
class Isracard(Money):
	pass
class Cash(Money):
	PARSERS = [
		lambda x: datetime.datetime.strptime(x, "%Y/%m/%d"),
		float,
		str,
		str
	]
	default_path = "~/Projects/Money/cash.csv"

class Combined(Money):
	def __init__(self, *preloaded_data):
		self.headers = BASE_HEADERS[:]
		self.data = []
		for d in preloaded_data:
			if not isinstance(d, Money):
				raise ValueError("%s is not an instance of Money" % d)
			# get the index of the headers we want to preserve
			wanted_headers = list(map(d.headers.index, self.headers))
			# convert from list of rows    (list of lists of columns)
			#         to   list of columns (list of lists of rows   )
			transposed_data = list(zip(*d.data))
			# get wanted columns and transpose back
			self.data += list(zip(*[transformed_data[i] for i in wanted_headers]))
		self.create_titles()
		self.create_friends_list()


if __name__ == '__main__':
	# a = Data()
	# # a.stats(2 if len(sys.argv) == 1 else int(sys.argv[1]))
	# a._display_month_by_date(2016, 12)
	# a._display_month_by_date(2017, 1)
	# a._display_month_by_date(2017, 2)
	# a._display_month_by_date(2017, 3)
	# # a._display_month_by_date(2016, 11)
	# # a._display_month_by_date(2016, 10)
	# # a._display_month_by_date(2016, 9)
	# # a._display_month_by_date(2016, 9, False)
	a = Visa()
	a._plot_text_money_title()
	a._plot_text_money_title(2017,8)
	a._plot_text_money_title(2017,9)
	a._plot_text_money_title(2017,10)
else:
	a = Visa()
	# import builtins
	# builtins.self = Data()
