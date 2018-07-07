#!/usr/bin/env python3

import os
import re
import sys

PATTERNS = {
	"date"     : re.compile(
		"<td data-title=\"text\\.TRAN_LIST\\.TABLE\\.TRAN_DATE\" sortable=\"\\&#39;OrderNumerator\\&#39;\" class=\"rowDateDisplay ng-binding\" data-title-text=\" \">(.*?)</td>"
	),
	"merchant" : re.compile(
		"<td data-title=\"text\\.TRAN_LIST\\.TABLE\\.MERCHANT\" sortable=\"\\&#39;MerchantName\\&#39;\" class=\"rowNameDisplay ng-binding\" data-title-text=\" \">(.*?)</td>"
	),
	"amount"   : re.compile(
		"<td data-title=\"text\\.TRAN_LIST\\.TABLE\\.TO_DEBIT_AMOUNT\" ng-bind-html=\"item\\.DebitAmountDisplay\" sortable=\"\\&#39;DebitAmount\\&#39;\" data-title-text=\" \" class=\"ng-binding\"><span class=\"number\"><span class=\"currency_symbol arimo \">(.*?)</span><span class=\"number-wrapper\"><span class=\"integer\">(\\d*)</span><span class=\"decimal_point\">\\.(\\d\\d)</span></span></span></td>"
	),
}

MERCHANTS = {
	"רשת כוורת בצהל" : "Shekem",
	"רשת כוורת בצה\"ל" : "Shekem",
	"קופי טיים"       : "Coffee",
	"סלטים"         : "Hatulia",
}

SUBJECTS = {
	"רשת כוורת בצהל" : "Shekem",
	"רשת כוורת בצה\"ל" : "Shekem",
	"קופי טיים"       : "Coffee",
	"סלטים"         : "NotNino",
}

def convert_data_to_csv(data_dict):
	return '\n'.join(
		"%s,-%s.%s,%s,%s" % (
			# date
			'/'.join(
				data_dict["date"][i].split('/')[::-1]
			),
			# amount - Shekels
			data_dict["amount"][i][1],
			# amount - Agorot
			data_dict["amount"][i][2],
			# subject
			SUBJECTS.get(data_dict["merchant"][i], "==="),
			# details
			MERCHANTS.get(data_dict["merchant"][i], "___" + data_dict["merchant"][i]),
		)
		for i in
		# range(len()) in reverse order
		range(len(data_dict["date"])-1, -1, -1)
	)

def main():
	for file_name in sys.argv[1:]:
		data = open(
			os.path.expandvars(
				os.path.expanduser(
					file_name
				))).read()

		# iterate the patterns
		data_dict = {}
		for k in PATTERNS:
			data_dict[k] = PATTERNS[k].findall(data)

		# safety checks
		if any(map(
			lambda x: x[0] != '₪',
			data_dict["amount"]
		)):
			return(bool(print("[!] a transaction with a new currency was found!")))

		if len(set(map(len, data_dict.items()))) != 1:
			return(bool(print("[!] every pattern resulted a different amount of results!")))

		open(
			os.path.expandvars(
				os.path.expanduser(
					file_name
				)) + ".csv", "w"
			).write(
				convert_data_to_csv(data_dict)
			)

if __name__ == '__main__':
	main()