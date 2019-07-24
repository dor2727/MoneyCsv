import utils
import datetime
from collections import defaultdict

###########################
### utils
###########################
def load_types(obj, exclude=[], *args):
	g = globals()
	for k,v in g.items():
		for t in [DataPlotter, TypePlotter, VisualPlotter]:
			if t not in exclude:
				if t in getattr(v, "mro", lambda:[]) () [1:]:
					setattr(obj, k, v(obj, *args))

def load_methods(obj, callers):
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
			self._exclude = caller._exclude + [self.__class__.mro()[1]]

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
		return self._plot(
			*self._summarize(
				*self._group(
					*self._get_data(
						year,
						month,
						bank_month,
					),
					include_salary,
				)
			),
			include_salary,
			title=self._data_name + " per " + self._group_name,
			*args,
			**kwargs,
		)

###########################
### base classes
###########################
class VisualPlotter(Plot):
	def _plot(self, data, titles, raw_data, salary, time_representation, amount_of_days, *args, **kwargs):
		raise NotImplimentedException()
		return True

class TypePlotter(Plot):
	def _summarize(self, data, titles, salary, time_representation, amount_of_days):
		raise NotImplimentedException()
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
		raise NotImplimentedException()
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

		friends_list = data.keys()
		grouped_data = [data[f] for f in friends_list]		
		# import pdb ; pdb.set_trace()

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
	def _summarize(self, data, titles, salary, time_representation, amount_of_days):
		return (
			# minus is for converting deposits into absolute value, where negative means savings
			[-sum(j.amount for j in i) for i in data],
			titles,
			data,
			salary,
			time_representation,
			amount_of_days
		)

class transactions(TypePlotter):
	def _summarize(self, data, titles, salary, time_representation, amount_of_days):
		return (
			[len(i) for i in data],
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
		utils.plot.bar(
			data,
			titles, # names
			title=kwargs["title"]
		)

class pie(VisualPlotter):
	def _plot(self, data, titles, raw_data, salary, time_representation, amount_of_days, *args, **kwargs):
		utils.plot.pie(
			# minus is for converting deposits into absolute value, where negative means savings
			[-x for x in data], # data
			titles, # names
			title=kwargs["title"]
		)

class text(VisualPlotter):
	@property
	def _data_name(self):
		return "summary"
	def _summarize(self, data, titles, salary, time_representation, amount_of_days):
		return (
			(
				[sum(j.amount for j in i) for i in data],
				[len(i) for i in data],
			),
			titles,
			data,
			salary,
			time_representation,
			amount_of_days
		)

	def _plot(self, data, titles, raw_data, salary, time_representation, amount_of_days, *args, **kwargs):
		import pdb; pdb.set_trace()
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
