import operator
from functools import reduce

from MoneyCsv.filters.content_filters import GroupFilter

# don't know if I should name them as "SomethingFilter", like the regular filter classes
# or "filter_something", to indicate that it is a specific case and not a general class

SalaryFilter = GroupFilter("Salary")

filter_shopping = reduce(
	operator.or_, [
		GroupFilter(i)
		for i in (
			"Aliexpress",
			"Amazon",
			"Shekem",
			"Supermarket",
		)
	]
)

filter_food = reduce(
	operator.or_, [
		GroupFilter(i)
		for i in (
			"Coffee",
			"Food",
			"NotNino",
			"Shekem",
			"Supermarket",
			"Wolt",
		)
	]
)

filter_self_gifts = reduce(
	operator.or_, [
		GroupFilter(i)
		for i in (
			"Book",
			"Gaming",
			"Puzzle",
			"Technology",
			"SelfPromotion",
			"Supermarket",
			"Sport",
		)
	]
)
