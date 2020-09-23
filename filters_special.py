from MoneyCsv.filters import *

# don't know if I should name them as "SomethingFilter", like the regular filter classes
# or "filter_something", to indicate that it is a specific case and not a general class

filter_shopping   = SubjectFilter("Aliexpress") | SubjectFilter("Amazon") | SubjectFilter("Shekem") | SubjectFilter("Supermarket")
filter_food       = SubjectFilter("Coffee") | SubjectFilter("Food") | SubjectFilter("NotNino") | SubjectFilter("Shekem") | SubjectFilter("Supermarket") | SubjectFilter("Wolt")
filter_self_gifts = SubjectFilter("Book") | SubjectFilter("Gaming") | SubjectFilter("Puzzle") | SubjectFilter("Technology") | SubjectFilter("SelfPromotion") | SubjectFilter("Supermarket") | SubjectFilter("Sport")
