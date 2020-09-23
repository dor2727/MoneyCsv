import os

from MoneyCsv.consts import *
from MoneyCsv.parsing import DataFile, DataFileList, DataItem_with_discount
from MoneyCsv.filters import *
import MoneyCsv.statistics

# create all DataFiles
visa = DataFile("Visa")
cash = DataFile("cash")
transactions = DataFile("Transactions")
isracard = DataFile("isracard",
	data_item_class=DataItem_with_discount
)

# join them
datafiles = DataFileList(visa, cash, transactions, isracard)

"""
test filters
	f = TimeFilter_Days(20) & AmountFilter(100)
	data = f.get_filtered_data(visa.data)
	print(len(data))
	print('\n'.join(map(str, data)))
"""

# f = TimeFilter_Year()
# data = f % visa.data
data = visa.data

# selected_time = f.get_selected_time()
groupedstats_params = {
	# "selected_time" : selected_time,
	"group_value"   : "money",
	"sort"          : "by_value",
}

gh = MoneyCsv.statistics.SubjectGroupedStats(
	data,
	category_name="Fuel",
	**groupedstats_params
)
print(gh.to_text())
import pdb; pdb.set_trace()

g = MoneyCsv.statistics.GroupedStats_Subject(
# g = MoneyCsv.statistics.GroupedStats_Games(
	data,
	**groupedstats_params
)

print(g.to_text())

for h in g.headers:
	gh = MoneyCsv.statistics.SubjectGroupedStats(
		data,
		category_name=h,
		**groupedstats_params
	)
	print("================")
	print("### %s ###" % h)
	print(gh.to_text())

# italy
# japan
# japan details

import pdb; pdb.set_trace()
