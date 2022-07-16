#!/usr/bin/env python3
import os
import pdb
import time
import datetime
import schedule
import threading

from telegram.ext import Updater, InlineQueryHandler, CommandHandler


from MoneyCsv.statistics import *
from MoneyCsv.parsing import DataFile, DataFileList, DataItem_with_discount
from MoneyCsv.consts import *
from MoneyCsv.filters import *
from MoneyCsv.filters_special import *

MAIN_FOLDER = os.path.dirname(__file__)
KEY_FILEPATH = os.path.join(TELEGRAM_DATA_DIRECTORY, "key")
CHAT_ID_FILEPATH = os.path.join(TELEGRAM_DATA_DIRECTORY, "chat_id")
LOG_FILE = open(os.path.join(MAIN_FOLDER, "log.log"), "a")

# utils
def read_file(filename):
	handle = open(filename)
	data = handle.read().strip()
	handle.close()
	return data

def log(s):
	print(s)
	LOG_FILE.write(s)
	LOG_FILE.write('\n')
	LOG_FILE.flush()

# wrappers
def log_command(func):
	def func_wrapper(*args, **kwargs):
		# each function is named "command_something"
		command_name = func.__name__[8:]

		if "scheduled" in kwargs:
			if kwargs["scheduled"]:
				log(f"    [*] scheduled command - {command_name}\t{time.asctime()}")
			kwargs.pop("scheduled")
		else:
			# args[1] is update
			if len(args) > 1 and args[1]:
				command_text = args[1]['message']['text']
			else:
				command_text = "None"
			log(f"    [*] got command - {command_text}\tcalling {command_name}\t{time.asctime()}")

		return func(*args, **kwargs)

	return func_wrapper

def void(*args, **kwargs):
	return None

"""
requires:
	1) self.user_chat_ids - a list of ints
	2) self.user_names    - a list of strings, in the same length as self.user_chat_ids
"""
def whitelisted_command(func):
	def func_wrapper(*args, **kwargs):
		self = args[0]
		if len(args) > 1 and args[1]:
			update = args[1]
			chat_id = update['message']['chat']['id']
			if chat_id == self._chat_id:
				log(f"[+] whitelist - success - {chat_id}")
			else:
				log(f"[-] whitelist - error - {chat_id}")
				log(str(update))
				log('\n')
				return void
		else:
			# scheduled command
			log(f"[*] whitelist - ignored (scheduled)")

		return func(*args, **kwargs)

	return func_wrapper



class TelegramServer(object):
	def __init__(self):
		# server initialization
		self._key = read_file(KEY_FILEPATH)
		self.updater = Updater(self._key, use_context=True)
		self.dp = self.updater.dispatcher

		self._chat_id = int(read_file(CHAT_ID_FILEPATH))

	def chat_id(self, update=None):
		if update:
			return update['message']['chat']['id']
		else:
			return self._chat_id

	def send_text(self, text, chat_id):
		self.updater.bot.sendMessage(
			chat_id,
			text
		)

	def send_image(self, image_file, chat_id, **kwargs):
		self.updater.bot.send_photo(
			chat_id,
			photo=image_file,
			**kwargs
		)

	def loop(self):
		print("[*] entering loop")
		self.updater.start_polling()
		self.updater.idle()

class TelegramCommands(object):
	def __init__(self):
		self.command_reload()
		self.add_all_handlers()

	def _command_name(self, c):
		return c[8:]

	def add_all_handlers(self):
		commands = filter(
			lambda s: s.startswith("command_"),
			dir(self)
		)

		for command_name in commands:
			self.dp.add_handler(CommandHandler(
				self._command_name(command_name),
				getattr(self, command_name)
			))

	def parse_args(self, context, *expected_types):
		result = []
		if context and context.args:
			try:
				for i in range(len(context.args)):
					result.append(expected_types[i](context.args[i]))
			except Exception as e:
				self.send_text(
					f"parse_args error: {e} ; args = {context.args}",
					# send it to me, not to the user (avoiding information disclosure)
					self.chat_id()
				)

		# fill default values, if needed
		for i in range(len(result), len(expected_types)):
			result.append(expected_types[i]())

		return result

	# debug
	@whitelisted_command
	@log_command
	def command_pdb(self, update=None, context=None):
		pdb.set_trace()

	@whitelisted_command
	@log_command
	def command_start(self, update, context):
		chat_id = self.chat_id(update)
		log("chat_id = %s" % chat_id)

	@whitelisted_command
	@log_command
	def command_list_commands(self, update=None, context=None):
		commands = filter(
			lambda s: s.startswith("command_"),
			dir(self)
		)

		self.send_text(
			'\n'.join(
				f"{self._command_name(c)} - {self._command_name(c)}"
				for c in commands
			),
			self.chat_id(update)
		)


	@whitelisted_command
	@log_command
	def command_reload(self, update=None, context=None):
		self.datafiles.reload()
		log(f"    [r] reloaded : {time.asctime()}")

		# if update is None - we are called from the scheduler
		# only answer the user if the user asks the reload
		if update is not None:
			self.send_text(
				"reload - done",
				self.chat_id(update)
			)


	#
	def filtered_time_command(self, f, update=None):
		g = GroupedStats_Subject(
			f % self.datafiles.data,
			selected_time=f.selected_time,
			group_value="money"
		)

		self.send_text(
			g.to_telegram(),
			self.chat_id(update)
		)

	@whitelisted_command
	@log_command
	def command_today(self, update=None, context=None):
		self.filtered_time_command(TimeFilter_Days(1), update)

	@whitelisted_command
	@log_command
	def command_week(self, update=None, context=None):
		self.filtered_time_command(TimeFilter_Days(7), update)

	@whitelisted_command
	@log_command
	def command_month(self, update=None, context=None):
		month, year = self.parse_args(context, int, int)
		self.filtered_time_command(TimeFilter_Month(month, year), update)

	@whitelisted_command
	@log_command
	def command_year(self, update=None, context=None):
		year, = self.parse_args(context, int)
		self.filtered_time_command(TimeFilter_Year(year), update)

	@whitelisted_command
	@log_command
	def command_yesterday(self, update=None, context=None):
		stop_time  = get_midnight( datetime.datetime.now() )
		start_time = get_midnight(
			stop_time
			 -
			datetime.timedelta(days=1)
		)

		self.filtered_time_command(
			TimeFilter_DateRange( start_time, stop_time ),
			update
		)

	@whitelisted_command
	@log_command
	def command_last_week(self, update=None, context=None):
		today = datetime.datetime.now()

		if WEEK_STARTS_AT_SUNDAY:
			weekday = today.weekday() + WEEK_STARTS_AT_SUNDAY
			if weekday == 7:
				weekday = 0
		else:
			weekday = today.weekday()
		this_sunday = get_midnight(today - datetime.timedelta(days=weekday))
		prev_sunday = this_sunday - datetime.timedelta(days=7)

		self.filtered_time_command(
			TimeFilter_DateRange( prev_sunday, this_sunday ),
			update
		)


	#
	def pie_command(self, g_cls, f, update=None):
		g = g_cls(
			f % self.datafiles.data,
			selected_time=f.selected_time,
			group_value="money"
		)

		# TODO:
		# this initializes self.headers_sorted, self.values_sorted
		# there should be a better (and automated) way to initialize them
		g.group()

		pie_file = g.to_pie()

		self.send_image(
			pie_file,
			self.chat_id(update)
		)

	@whitelisted_command
	@log_command
	def command_pie_week(self, update=None, context=None):
		self.pie_command(GroupedStats_Subject, TimeFilter_Days(7), update)

	@whitelisted_command
	@log_command
	def command_pie_month(self, update=None, context=None):
		month, year = self.parse_args(context, int, int)
		self.pie_command(GroupedStats_Subject, TimeFilter_Month(month, year), update)

	@whitelisted_command
	@log_command
	def command_pie_friends(self, update=None, context=None):
		month, = self.parse_args(context, int)
		self.pie_command(GroupedStats_Friend, TimeFilter_Month(month), update)

	@whitelisted_command
	@log_command
	def command_pie_shopping(self, update=None, context=None):
		month, = self.parse_args(context, int)
		def g(data, *args, **kwargs):
			return FilteredGroupedStats(data, filter_shopping, *args, **kwargs)
		self.pie_command(g, TimeFilter_Month(month), update)


class TelegramScheduledCommands(object):
	def __init__(self):
		self.schedule_commands()

	def schedule_commands(self):
		schedule.every().day.at("05:00").do(
			self.command_reload,
			scheduled=True
		)

		# daily log
		schedule.every().day.at("08:00").do(
			self.command_yesterday,
			scheduled=True
		)

		# weekly log
		schedule.every().sunday.at("08:00").do(
			self.command_last_week,
			scheduled=True
		)
		schedule.every().sunday.at("08:00").do(
			self.command_pie_week,
			scheduled=True
		)

		def monthly_report():
			if datetime.datetime.now().day == 1:
				self.command_month(scheduled=True)
				self.command_pie_month(scheduled=True)
		schedule.every().day.at("08:00").do(
			monthly_report,
		)


		def run_scheduler():
			while True:
				schedule.run_pending()
				time.sleep(60*60*0.5)

		threading.Thread(target=run_scheduler).start()

class TelegramAPI(TelegramServer, TelegramCommands, TelegramScheduledCommands):
	def __init__(self):
		TelegramServer.__init__(self)
		self.init_datafiles()
		TelegramCommands.__init__(self)
		TelegramScheduledCommands.__init__(self)

	def init_datafiles(self):
		self.visa = DataFile("Visa")
		self.cash = DataFile("cash")
		self.transactions = DataFile("Transactions")
		self.isracard = DataFile("isracard",
			data_item_class=DataItem_with_discount
		)

		self.datafiles = DataFileList(self.visa, self.cash, self.transactions, self.isracard)



def main():
	log(f"----------------")
	now = datetime.datetime.now().strftime("%Y/%m/%d_%H:%M")
	log(f"[*] Starting: {now}")

	t = TelegramAPI()
	t.loop()
	LOG_FILE.close()

if __name__ == '__main__':
	main()
