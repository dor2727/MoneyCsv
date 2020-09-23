from MoneyCsv.cli import main
from MoneyCsv.parsing import DataFile, DataFileList, DataItem_with_discount

if __name__ == '__main__':
	visa = DataFile("Visa")
	cash = DataFile("cash")
	transactions = DataFile("Transactions")
	isracard = DataFile("isracard",
		data_item_class=DataItem_with_discount
	)

	# join them
	datafiles = DataFileList(visa, cash, transactions, isracard)

	print(main(datafiles))
	