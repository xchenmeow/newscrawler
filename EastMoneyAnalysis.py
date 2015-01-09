import pandas as pd
import datetime


def startwith036(string):
	isdigit = string.isdigit()
	a = ['0','3','6']
	is036 = any([string.startswith(i) for i in a])
	return isdigit and is036

def lasttime2date(lasttime):
	pass


def isvacation(date):
	vacationlist = [datetime.datetime(2014,1,1),datetime.datetime(2014,1,30),datetime.datetime(2014,1,31),\
	datetime.datetime(2014,2,3),datetime.datetime(2014,2,4),datetime.datetime(2014,2,5),datetime.datetime(2014,5,1),\
	datetime.datetime(2014,5,2),datetime.datetime(2014,6,2),datetime.datetime(2014,9,8),datetime.datetime(2014,10,1),\
	datetime.datetime(2014,10,2),datetime.datetime(2014,10,3),datetime.datetime(2014,10,6),datetime.datetime(2014,10,7),\
	datetime.datetime(2015,1,1),datetime.datetime(2015,1,2)]
	if date.weekday() == 5 or date.weekday() == 6:
		return True
	else:
		return date in vacationlist
 
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
for i in range(len(diffkeys)):
	print keys[int(diffkeys[i][4:])][1] 
	m = grouprev.sort(diffkeys[i],ascending=False)
	t = m.index[0:10]
	# print t
	print m[diffkeys[i]][0:10]

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
