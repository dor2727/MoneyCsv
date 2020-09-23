import os

from MoneyCsv.consts import *
from MoneyCsv.parsing import DataFile, DataFileList, DataItem_with_discount

visa = DataFile("Visa")
cash = DataFile("cash")
transactions = DataFile("Transactions")
isracard = DataFile("isracard",
	data_item_class=DataItem_with_discount
)

datafiles = DataFileList(visa, cash, transactions, isracard)

# italy
# japan
# japan details

import pdb; pdb.set_trace()
