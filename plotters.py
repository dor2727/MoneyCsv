import utils
import calendar
import datetime
from collections import defaultdict

###########################
### utils
###########################
def load_types(obj, exclude=[], *args):
	"""
	iterate every object
	search for plotters
	exclude plotters according to the excludion list

	try calling the "mro" method (which is available to classes, so there
		is a fail-safe of a lambda function to return the same type of
		return value as the mro method)
	search only in the second or later item in the list ("[1:]")
		to exclude the type itself

	use setattr to dynamically add the wanted plotter to the object
	"""
	g = globals()
	for k,v in g.items():
		for t in [DataPlotter, TypePlotter, VisualPlotter]:
			if t not in exclude:
				if t in getattr(v, "mro", lambda:[]) () [1:]:
					setattr(obj, k, v(obj, *args))

def load_methods(obj, callers):
	"""
	dynamically inherit all the methods from the previous callers
	"""
	for caller in callers:
		for i in dir(caller):
			if i[0] == '_' and i[1] != '_' and i != "_exclude":
				try:
					setattr(obj, i, getattr(caller, i))
				except:
					pass


###########################
### main class
###########################
class Plot(object):
	def __init__(self, caller=None, get_data=None, prev_callers=[]):
		if caller is None:
			self._exclude = []
		else:
			# add the "father class" of the current class to the exclution list
			# so that all the other similar plotters will be excluded
			# 
			# the first is the class itself
			# the second (or more) are its "father classes"
			# the second from the end is "Plot"
			# the last is "object"
			father_class = self.__class__.mro()[1:-2]

			self._exclude = caller._exclude + father_class

		if get_data is not None:
			self._get_data = get_data

		prev_callers = prev_callers + [caller]

		load_types(self, self._exclude, self._get_data, prev_callers)

		load_methods(self, prev_callers)

	# def _sort(self, keys, values, *args, **kwargs):
	# 	temp = [(friends_list[i], grouped_data[i]) for i in range(len(friends_list))]
	# 	temp = sorted(temp, key=lambda x:sum(i.amount for i in x[1]))
	# 	friends_list, grouped_data = list(zip(*temp))

	# 	return keys, values, *args, **kwargs

	def __call__(self, year=None, month=None, bank_month=True, include_salary=False, *args, **kwargs):
		if "title" not in kwargs:
			kwargs["default_title"] = self._data_name + " per " + self._group_name
		return self._plot(
			*self._summarize(
				*self._group(
					*self._get_data(
						year,
						month,
						bank_month,
					),
					include_salary,
				),
				amount=kwargs.get("amount", None),
			),
			include_salary,
			*args,
			**kwargs,
		)

###########################
### base classes
###########################
class VisualPlotter(Plot):
	def _plot(self, data, titles, raw_data, salary, time_representation, amount_of_days, *args, **kwargs):
		"""

		data                : list of integers, its length is determined by len(titles)
		titles              : set of strings (unchanged)
		raw_data            : list of lists of statistics.Data objects (unchanged)
		salary              : list of statistics.Data objects (unchanged)
		time_representation : string (unchanged)
		amount_of_days      : int (unchanged)
		*args               : list. the first is "include_salary" which is a boolean
								the rest are coming from the caller
		**kwargs            : dict. the first is "title" which is a string
								the rest are coming from the caller
								most of it is calls for matplotlib
		"""
		raise NotImplementedError()
		return True

class TypePlotter(Plot):
	def _summarize(self, data, titles, salary, time_representation, amount_of_days, amount=None):
		"""
		data                : list of lists of statistics.Data objects
		titles              : set of strings
		salary              : list of statistics.Data objects (unchanged)
		time_representation : string (unchanged)
		amount_of_days      : int (unchanged)
		amount              : int (or None) - amount of items to display
		"""
		raise NotImplementedError()
		return (
			summarized_data,
			titles,
			raw_data,
			salary,
			time_representation,
			amount_of_days
		)
	@property
	def _data_name(self):
		return self.__class__.__name__

class DataPlotter(Plot):
	def _group(self, items, salary, time_representation, amount_of_days, include_salary):
		"""
		items               : list of statistics.Data objects
		salary              : list of statistics.Data objects
		time_representation : string
			this will mostly be forwarded
		amount_of_days      : int
		include_salary      : bool
		"""
		raise NotImplementedError()
		return (
			grouped_data,
			titles,
			salary,
			time_representation,
			amount_of_days
		)
	@property
	def _group_name(self):
		return self.__class__.__name__


###########################
### Data plotters
###########################
class title(DataPlotter):
	def _group(self, items, salary, time_representation, amount_of_days, include_salary):
		titles = set(d.subject for d in items)
		if include_salary:
			titles.update(d.subject for d in salary)

		titles_index = {t:i for i,t in enumerate(titles)}


		# create n empty lists
		data = [[] for i in titles]

		# append each item for the list of its title
		for d in items:
			data[titles_index[d.subject]].append(d)
		
		if include_salary:
			for d in salary:
				data[titles_index[d.subject]].append(d)

		return (
			data,
			titles,
			salary,
			time_representation,
			amount_of_days
		)

# 01/01/01 is Monday
DAYS = [datetime.datetime(1,1,i).strftime("%a") for i in range(1,7+1)]
class weekday(DataPlotter):
	def _group(self, items, salary, time_representation, amount_of_days, include_salary):
		data = [[] for i in range(7)]

		for d in items:
			data[d.date.weekday()].append(d)
		
		if include_salary:
			for d in salary:
				data[d.date.weekday()].append(d)

		# every day, starting at Sunday, where Monday == 0
		return (
			[data[6]] + data[:6],
			[DAYS[t] for t in [6,0,1,2,3,4,5]],
			salary,
			time_representation,
			amount_of_days
		)

class friends(DataPlotter):
	def _group(self, items, salary, time_representation, amount_of_days, include_salary):
		data = defaultdict(list)
		for d in items:
			for f in d.friends:
				data[f].append(d)

		friends_list = list(data.keys())
		grouped_data = [data[f] for f in friends_list]		

		return (
			grouped_data,
			friends_list,
			salary,
			time_representation,
			amount_of_days
		)


###########################
### Type Plotters
###########################
class money(TypePlotter):
	def _summarize(self, data, titles, salary, time_representation, amount_of_days, amount=None):
		# minus is for converting deposits into absolute value, where negative means savings
		summarized_data = [-sum(j.amount for j in i) for i in data]
		if amount:
			# group summarized_data & titles together
			temp = list(zip(summarized_data, titles))
			# sort by summarized data
			temp.sort(key=lambda x:x[0], reverse=True)
			# cut exceeding data
			temp = temp[:amount]
			# unpack back into 2 lists
			summarized_data, titles = zip(*temp)

		return (
			summarized_data,
			titles,
			data,
			salary,
			time_representation,
			amount_of_days
		)

class transactions(TypePlotter):
	def _summarize(self, data, titles, salary, time_representation, amount_of_days, amount=None):
		summarized_data = [len(i) for i in data]
		if amount:
			# group summarized_data & titles together
			temp = list(zip(summarized_data, titles))
			# sort by summarized data
			temp.sort(key=lambda x:x[0], reverse=True)
			# cut exceeding data
			temp = temp[:amount]
			# unpack back into 2 lists
			summarized_data, titles = zip(*temp)
		
		return (
			summarized_data,
			titles,
			data,
			salary,
			time_representation,
			amount_of_days
		)


###########################
### Visual Plotters
###########################
class bar(VisualPlotter):
	def _plot(self, data, titles, raw_data, salary, time_representation, amount_of_days, *args, **kwargs):
		if "title" in kwargs:
			title = kwargs["title"]
		elif "default_title" in kwargs:
			title = kwargs["default_title"] + " at " + time_representation
		else:
			title = time_representation

		utils.plot.bar(
			data,
			titles, # names
			title=title,
		)

class pie(VisualPlotter):
	def _plot(self, data, titles, raw_data, salary, time_representation, amount_of_days, *args, **kwargs):
		if "title" in kwargs:
			title = kwargs["title"]
		elif "default_title" in kwargs:
			title = kwargs["default_title"] + " at " + time_representation
		else:
			title = time_representation

		utils.plot.pie(
			data,
			titles, # names
			title=title,
		)

class text(VisualPlotter):
	@property
	def _data_name(self):
		return "summary"
	def _summarize(self, data, titles, salary, time_representation, amount_of_days, amount=None):
		summarized_data = (
			[sum(j.amount for j in i) for i in data],
			[len(i) for i in data],
		)
		if amount:
			summarized_data = summarized_data[:amount]

		return (
			summarized_data,
			titles,
			data,
			salary,
			time_representation,
			amount_of_days
		)

	def _plot(self, data, titles, raw_data, salary, time_representation, amount_of_days, *args, **kwargs):
		money, transactions = data
		total_money        = sum(money)
		total_transactions = sum(transactions)
		
		print(time_representation)

		# print basic statistics
		print("  items per day = %.2f" % (total_transactions / amount_of_days    ))
		print("  days per item = %.2f" % (amount_of_days     / total_transactions))
		print("  avg per day   = %.2f" % (total_money        / amount_of_days    ))
		print("  avg per item  = %.2f" % (total_money        / total_transactions))

		titles_index = {t:i for i,t in enumerate(titles)}

		for t in titles:
			print("    %-10s (%3d) : %7.1f (%02d%%)" % (
				t,
				transactions[titles_index[t]],
				money       [titles_index[t]],
				money       [titles_index[t]] / total_money * 100
			))

		print("    " + '-'*32)
		print("    %-10s (%3d) : %7.1f [%5d]" % (
			"Total",
			total_transactions,
			total_money,
			sum(i.amount for i in salary)
		))
		print()

class stats(VisualPlotter, DataPlotter, TypePlotter):
	# shortcuts
	# changed "bank_month" default from True to False
	def __call__(self, year=None, month=None, bank_month=False, include_salary=False, *args, **kwargs):
		self.__reverse = kwargs.get("reverse", False)
		return super().__call__(year, month, bank_month, include_salary, *args, **kwargs)
	call = plot = __call__ 

	def _group(self, items, salary, time_representation, amount_of_days, include_salary):
		# a list of tuples of (year:int, month:int)
		months = list(set((i[0].year, i[0].month) for i in items))
		months.sort(key=lambda x: x[0]*12 + x[1], reverse=self.__reverse)

		items_per_month = {}
		for m in months:
			items_per_month[m] = list()
		for i in items:
			# the key is a tuple of the year and month
			items_per_month[(i[0].year, i[0].month)].append(i)

		return (
			items_per_month,
			months,
			salary,
			time_representation,
			amount_of_days
		)


	def _summarize(self, data, months, salary, time_representation, amount_of_days, amount=None):
		data_summary_per_month = []
		titles = self.__get_all_titles(data)

		for m in months:
			
			month_total     = sum(i[1] for i in data[m])
			amount_of_days  = calendar.monthrange(*m)[1]
			amount_of_items = len(data[m])

			data_summary_per_month.append(
				{
					"title"             : data[m][0][0].strftime("%Y - %m (%B)"),
					"amount_of_days"    : amount_of_days,
					"amount_of_items"   : amount_of_items,
					"month_total"       : month_total,
					"items per day"     : (amount_of_items / amount_of_days),
					"days per item"     : (amount_of_days / amount_of_items),
					"avg per day"       : (month_total / amount_of_days    ),
					"avg per item"      : (month_total / amount_of_items   ),
					"summary_per_title" : self.__generate_summary_per_title(data[m], titles, month_total),
				}
			)

		return (
			data_summary_per_month,
			months,
			data,
			salary,
			time_representation,
			amount_of_days
		)

	def __get_all_titles(self, data):
		titles = set()
		for m in data:
			for i in data[m]:
				titles.add(i.subject)

		return titles
	def __generate_summary_per_title(self, data, titles, month_total):
		summary_per_title = []
		max_title_lenght = max(len(t) for t in titles)
		for t in titles:
			summary_per_title.append("    %s (%2d) : %8.2f (%02d%%)" % (
				"%%-%ds" % max_title_lenght % t,
				len(list(filter(
					lambda x: x[2] == t,
					data
				))),
				sum(i[1] for i in data if i[2] == t),
				sum(i[1] for i in data if i[2] == t) / month_total * 100
			))
		return summary_per_title

	def _plot(self, data, titles, raw_data, salary, time_representation, amount_of_days, *args, **kwargs):
		for month in data:
			print(month["title"])
			# print basic statistics
			print("  items per day = %.2f" % month["items per day"])
			print("  days per item = %.2f" % month["days per item"])
			print("  avg per day   = %.2f" % month["avg per day"  ])
			print("  avg per item  = %.2f" % month["avg per item" ])

			# print data per title
			for i in month["summary_per_title"]:
				print(i)

			print("    " + '-'*29)

			print("    %-10s (%2d) : %8.2f" % (
				"Total",
				month["amount_of_items"],
				month["month_total"],
			))
			print()

		
