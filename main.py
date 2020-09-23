#!/usr/bin/env python3.8

import statistics

# def main():
# 	# a = Data()
# 	# # a.stats(2 if len(sys.argv) == 1 else int(sys.argv[1]))
# 	# a._display_month_by_date(2016, 12)
# 	# a._display_month_by_date(2017, 1)
# 	# a._display_month_by_date(2017, 2)
# 	# a._display_month_by_date(2017, 3)
# 	# # a._display_month_by_date(2016, 11)
# 	# # a._display_month_by_date(2016, 10)
# 	# # a._display_month_by_date(2016, 9)
# 	# # a._display_month_by_date(2016, 9, False)
# 	a = Visa()
# 	a._plot_text_money_title()
# 	# a._plot_text_money_title(2017,8)
# 	# a._plot_text_money_title(2017,9)
# 	# a._plot_text_money_title(2017,10)
# 	a._plot_text_money_title(2018,5)

def main():
	visa = statistics.Visa()
	visa._plot_text_money_title()
	visa._plot_text_money_title(2018,5)


if __name__ == '__main__':
	main()
