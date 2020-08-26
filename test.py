import os

from MoneyCsv.consts import *
from MoneyCsv.parsing import DataFile, DataFileList, DataItem_with_discount

visa = DataFile(
	path=os.path.join(DEFAULT_DATA_DIRECTORY, "Visa.txt"),
	name="visa",
)
cash = DataFile(
	path=os.path.join(DEFAULT_DATA_DIRECTORY, "cash.csv"),
	name="cash",
)
transactions = DataFile(
	path=os.path.join(DEFAULT_DATA_DIRECTORY, "Transactions.csv"),
	name="transactions",
)
isracard = DataFile(
	path=os.path.join(DEFAULT_DATA_DIRECTORY, "isracard.csv"),
	name="isracard",
	data_item_class=DataItem_with_discount
)

datafiles = DataFileList(visa, cash, transactions, isracard)

# italy
# japan
# japan details
