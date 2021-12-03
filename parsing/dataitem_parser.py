import os
import csv
import datetime

from MoneyCsv.parsing.consts import *
from MoneyCsv.parsing.parse_exception import ParseError


class DataItemParser(object):
	"""
	comment lines are either empty lines or lines starting with '#'

	expected input for __init__ is a list of items in the following order:
		date        (str) (yyyy/mm/dd)
		start_time  (str) (hh:mm)
		end_time    (str) ('e'hh:mm) (e for End time, d for Duration)
		group       (str) (should start with a capital letter)
		description (str)

	the parsing should go as follows:
		first, this class should call each parser to store each value in its place
		then, the caller should iterate the 'reevaluate' method for each data object,
			with its 2 neighbors
		this way, place holders such as "My date is the same as the previous object date"
			(which is written as "----/--/--") will be evaluated
	"""
	def __init__(self, items, headers, file_name="Unknown", line="??"):
		# debug information
		self._file_name = file_name
		self._line = line

		if self._check_if_comment(items):
			return

		self._headers = headers
		self._items = {
			key: self.PARSERS[key](value)
			for key, value in zip(headers, items)
		}

		self.set_defaults()

	def __repr__(self):
		if self.is_comment:
			return "# A comment"

		return "%s : %s%s : %s : %-14s" % (
			self._format_date(),
			self._format_amount(),
			self._format_currency(),
			self._format_group(),
			self._format_description(),
		)


	def _check_if_comment(self, items):
		"""
		comment lines are either empty lines or lines starting with '#'
		"""
		if not items:
			# if items is an empty list - [] - then the line is empty
			self.is_comment = True
		elif items[0][0] == '#':
			self.is_comment = True
		else:
			self.is_comment = False

		return self.is_comment

	def _format_error(self, text):
		return f"[!] {text} in file \"{self._file_name}\" : {self._line} : < {self} >"


	#
	# first parse iteration
	#
	def _parser_date(self, s):
		"""
		after this initial parsing, self.date will be:
			- str, if it was a special placeholder in the csv
			- datetime object, if it was a regular date value
		"""
		if s in SPECIAL_DATE_FORMATS:
			self.date = s
		else:
			self.date = datetime.datetime.strptime(s, "%Y/%m/%d")

		return self.date
	def _parser_amount(self, s):
		self.amount = float(s)
		return self.amount
	def _parser_currency(self, s):
		self.currency = s
		return s
	def _parser_group(self, s):
		self.group = s
		return s
	def _parser_description(self, s):
		self.description = s
		return s

	def _parser_prediscount_amount(self, s):
		self.prediscount_amount = float(s)
		return self.prediscount_amount
	def _parser_amount_converted(self, s):
		self.amount_converted = s
		return s
	def _parser_payment(self, s):
		self.payment = s
		return s
	def _parser_frequency(self, s):
		self.frequency = s
		return s

	@property
	def PARSERS(self):
		"""
		returns a list of parsers by order
		"""
		return {
			"Date": self._parser_date,
			"Amount": self._parser_amount,
			"Currency": self._parser_currency,
			"Group": self._parser_group,
			"Description": self._parser_description,
			"PreDiscount_Amount": self._parser_prediscount_amount,
			"Payment": self._parser_payment,
			"Amount_Converted": self._parser_amount_converted,
			"Frequency": self._parser_frequency,
		}

	def set_defaults(self):
		if not hasattr(self, "currency"):
			self.currency = "nis"

		if not hasattr(self, "prediscount_amount"):
			self.prediscount_amount = self.amount

	@property
	def currency_symbol(self):
		return CURRENCY_SYMBOL.get(self.currency, '?')
	

	def _format_date(self):
		if not hasattr(self, "date"):
			return "????/??/??"

		if type(self.date) is str:
			return self.date
		else:
			return self.date.strftime("%Y/%m/%d")
	def _format_amount(self):
		# 4 digit . 2 digit
		return f"{self.amount:7.2f}"
	def _format_currency(self):
		return self.currency_symbol
	def _format_group(self):
		return getattr(self, "group", "???")
	def _format_description(self):
		return getattr(self, "description", "???")

	#
	# second parse iteration
	#
	def _reevaluate_date(self, prev, next=None):
		if type(self.date) is str:
			if self.date == COPY_LAST_DATE:
				self.date = prev.date
			elif self.date == ADD_LAST_DATE:
				self.date = prev.date + datetime.timedelta(days=1)
	def reevaluate(self, p, n):
		"""
		reevaluates the date of this object
		this calls the second parsing functions
		p & n stands for previous & next items
			(I avoided calling 'n' "next" because it is a builtin python function)
		"""

		self._reevaluate_date(p, n)

	def is_fully_parsed(self):
		"""
		checks whether every object has the type it is supposed to have
		"""
		return all([
			type(self.date              ) is datetime.datetime,
			type(self.amount            ) is float,
			type(self.prediscount_amount) is float,
			type(self.currency          ) is str,
			type(self.group             ) is str,
			type(self.description       ) is str,
			self.prediscount_amount >= self.amount,
		])
