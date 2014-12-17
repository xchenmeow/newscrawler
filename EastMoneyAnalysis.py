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
	pass

dfPostInfo = pd.read_csv('EastMoneyArchive.csv')
dfPostInfo = dfPostInfo.drop_duplicates()
dfClkRev = pd.read_csv('EastMoneyClkRev.csv')
dfClkRev = dfClkRev.drop_duplicates()
href = dfClkRev['href']
ticker = [item.split(',')[1] for item in dfClkRev['href']]
postid = [item.split(',')[2][0:-5] for item in dfClkRev['href']]
# TODO
# today: yesterday 09:00 to today 09:00
date = [item[0:-9] for item in dfClkRev['lasttime']]
dfclk = pd.DataFrame(index=range(len(dfClkRev.index)))
dfrev = pd.DataFrame(index=range(len(dfClkRev.index)))
# df['postid'] = postid
dfclk['ticker'] = ticker
dfclk['date'] = date
# df['rev'] = dfClkRev['rev']
dfclk['clk'] = dfClkRev['clk']
dfrev['ticker'] = ticker
dfrev['date'] = date
dfrev['rev'] = dfClkRev['rev']
idx = [i for i in range(len(ticker)) if not startwith036(ticker[i])]
dfrevdropstr = dfrev.drop(dfrev.index[idx])
grouprev = dfrevdropstr.groupby(['ticker','date']).sum().unstack().fillna(value=0)
# TODO
# group Sat and Sun with Fri
key = list(grouprev)
for i in range(len(key)-1):
	diff = 'diff'+str(i)
	grouprev[diff] = grouprev[key[i+1]]-grouprev[key[i]]
	# TODO
	# as percentage???
	# grouprev = grouprev.fillna(0)
for i in range(len(key)-1):
	diff = 'diff'+str(i)
	print key[i+1][1]
	m = grouprev.sort(diff,ascending=False)
	t = m.index[0:10]
	print t
	print m[diff][0:10]

dfclkdropstr = dfclk.drop(dfclk.index[idx])
groupclk = dfclkdropstr.groupby(['ticker','date']).sum().unstack().fillna(value=0)
key = list(groupclk)
for i in range(len(key)-1):
	diff = 'diff'+str(i)
	groupclk[diff] = groupclk[key[i+1]]-groupclk[key[i]]
for i in range(len(key)-1):
	diff = 'diff'+str(i)
	# print key[i+1][1]
	m = groupclk.sort(diff)
	t = m.index[0:10]
	# print t