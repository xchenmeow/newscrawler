
import urllib2
from bs4 import BeautifulSoup


urlstr = 'http://finance.yahoo.com'
soup = BeautifulSoup(urllib2.urlopen(urlstr).read())
rows = soup.find_all('p')
text = []
for row in rows:
	try:
		if row['class'] == ['M-0', 'Fw-b', 'Lh-11', 'MouseOver-TextDecoration']:
			text.append(row.string)
		if row['class'] == ['summary', 'mt-xxs']:
			text.append(row.string)
	except KeyError:
		continue


## TODO: write text to csv if it is not in that csv
# and then find the frequency of each product(stock, futures, options etc)
# calculate the sentiment score of each news for each product
# compare the sentiment score with the previous scores(one day ago)
# max difference is the trending product