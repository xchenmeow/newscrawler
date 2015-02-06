import pandas as pd
import datetime
import os
import csv
import GetStockInfo

def startwith036(string):
	isdigit = string.isdigit()
	a = ['0','3','6']
	is036 = any([string.startswith(i) for i in a])
	return isdigit and is036

def lasttime2date(lasttime):
	pass


def isvacation(date):
	vacationlist2014 = [datetime.datetime(2014,1,1),datetime.datetime(2014,1,30),datetime.datetime(2014,1,31),\
	datetime.datetime(2014,2,3),datetime.datetime(2014,2,4),datetime.datetime(2014,2,5),datetime.datetime(2014,5,1),\
	datetime.datetime(2014,5,2),datetime.datetime(2014,6,2),datetime.datetime(2014,9,8),datetime.datetime(2014,10,1),\
	datetime.datetime(2014,10,2),datetime.datetime(2014,10,3),datetime.datetime(2014,10,6),datetime.datetime(2014,10,7)]
	vacationlist2015 = [datetime.datetime(2015,1,1),datetime.datetime(2015,1,2),datetime.datetime(2015,2,18),\
	datetime.datetime(2015,2,19),datetime.datetime(2015,2,20),datetime.datetime(2015,2,23),datetime.datetime(2015,2,24),\
	datetime.datetime(2015,4,6),datetime.datetime(2015,5,1)]
	vacationlist = vacationlist2014+vacationlist2015
	if date.weekday() == 5 or date.weekday() == 6:
		return True
	else:
		return date in vacationlist

def tickernum2ticker(tickernum):
	if tickernum.startswith('6'):
		return 'sh'+tickernum
	elif tickernum.startswith('0') or tickernum.startswith('3'):
		return 'sz'+tickernum
	else:
		return tickernum

def findlasttradingday(todaysdate):
	yesterday = todaysdate - datetime.timedelta(days=1)
	if isvacation(yesterday):
		return findlasttradingday(yesterday)
	else:
		return yesterday

print findlasttradingday(datetime.datetime(2015,1,5))

dfPostInfo = pd.read_csv('EastMoneyArchive.csv')
dfPostInfo = dfPostInfo.drop_duplicates()
dfClkRev = pd.read_csv('EastMoneyClkRev.csv')
dfClkRev = dfClkRev.drop_duplicates()
href = list(dfClkRev['href'])
for item in href:
	try:
		a = item.split(',')[1]
	except IndexError:
		print item
ticker = [item.split(',')[1] for item in href] 
postid = [item.split(',')[2][0:-5] for item in href]
# TODO
# today: yesterday 09:00 to today 09:00
date = [item[0:-9] for item in dfClkRev['lasttime']]
dfclk = pd.DataFrame(index=range(len(dfClkRev.index)))
dfrev = pd.DataFrame(index=range(len(dfClkRev.index)))
dfclk['ticker'] = ticker
dfclk['date'] = date
dfclk['clk'] = dfClkRev['clk']
dfrev['ticker'] = ticker
dfrev['date'] = date
dfrev['rev'] = dfClkRev['rev']
idx = [i for i in range(len(ticker)) if not startwith036(ticker[i])]
dfrevdropstr = dfrev.drop(dfrev.index[idx])

# TODO
# if id is identical, change rev to deltarev, clk to deltaclk
# e.g.
# id=000001, lasttime=2015/01/12 15:35:00, rev=3, clk=108
# id=000001, lasttime=2015/01/12 15:35:00, rev=5, clk=136
# change the second one to rev=2 and clk=28

grouprev = dfrevdropstr.groupby(['ticker','date']).sum().unstack().fillna(value=0)
keys = list(grouprev) 
diffkeys = []
for i in range(1,len(keys)):
	if not isvacation(datetime.datetime.strptime(keys[i][1],'%Y-%m-%d')):
		diff = 'diff'+str(i) 
		diffkeys.append(diff)
		grouprev[diff] = grouprev[keys[i]]-grouprev[keys[i-1]]
	else:
		grouprev[keys[i]] = grouprev[keys[i-1]] 
	# TODO
	# as percentage???


# TODO
# only find open price for tickers whose key is the last trading day
# only append data do not exists in file

today = datetime.date.today()
outputfilename = 'EastMoneyStatsTickers.csv'
N = 20000
outputframe = pd.DataFrame(range(10))
for i in range(len(diffkeys)):
	datekey = keys[int(diffkeys[i][4:])][1]
	m = grouprev.sort(diffkeys[i],ascending=False)
	output = m[diffkeys[i]][0:10]
	outputframe['ticker'] = [tickernum2ticker(tickernum) for tickernum in output.index]
	outputframe['openprice'] = [GetStockInfo.stockInfo(ticker).getfirstlevelinfo().open for ticker in outputframe['ticker']]
	outputframe['quantity'] = [N / openprice if openprice > 0 else 0 for openprice in outputframe['openprice']]
	if not os.path.exists(outputfilename): 
		with open(outputfilename, 'wb') as f:
			writer = csv.writer(f)
			writer.writerow([datekey])
			outputframe.to_csv(f, header=True, index=False)
	else:
		with open(outputfilename, 'ab') as f:
			writer = csv.writer(f)
			writer.writerow([datekey])
			outputframe.to_csv(f, header=True, index=False)
 


dfclkdropstr = dfclk.drop(dfclk.index[idx])
groupclk = dfclkdropstr.groupby(['ticker','date']).sum().unstack().fillna(value=0)
keys = list(groupclk)
for i in range(len(keys)-1):
	diff = 'diff'+str(i)
	groupclk[diff] = groupclk[keys[i+1]]-groupclk[keys[i]]
for i in range(len(keys)-1):
	diff = 'diff'+str(i)
	# print keys[i+1][1]
	m = groupclk.sort(diff,ascending=False)
	t = m.index[0:10]
	# print t
	# print m[diff][0:10]
