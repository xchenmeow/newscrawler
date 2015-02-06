import requests


class firstLevel(object):
	'''data structure
	holding openprice, lastclose, currentprice, high, low, bid1, ask1, volume, amount'''
	def __init__(self, openprice, lastclose, currentprice, high, low, bid1, ask1, volume, amt):
		self.open = openprice
		self.lastclose = lastclose
		self.currentprice = currentprice
		self.high = high
		self.low = low
		self.bid1 = bid1
		self.ask1 = ask1
		self.volume = volume
		self.amt = amt

class secBid(object):
	'''data structure
	holding bid volome includes bidvolume1 to bidvolume5 as a list
	bid includes bid1 to bid5 as a list'''
	def __init__(self, bidvolume, bid):
		self.bidvolume = bidvolume
		self.bid = bid

class secAsk(object):
	'''data structure
	holding ask volome includes askvolume1 to askvolume5 as a list
	ask includes ask1 to ask5 as a list'''
	def __init__(self, askvolume, ask):
		self.askvolume = askvolume
		self.ask = ask

class stockInfo(object):
	'''get stock information from sinajs
	including stock name, firstlevel information, bid information, askinformation, date and time'''
	def __init__(self, ticker):
		self.ticker = ticker
	def getcontent(self):
		baseurl = 'http://hq.sinajs.cn/&list='
		ticker = self.ticker
		url = baseurl + ticker
		resp = requests.get(url)
		content = resp.text
		return content.split('"')[1]
	def getname(self):
		content = self.getcontent()
		return content.split(',')[0]
	def getfirstlevelinfo(self):
		content = self.getcontent()
		firstlist = content.split(',')[1:10]
		firstlist = map(float, firstlist)
		(o,lc,cp,h,l,b1,a1,v,a) = tuple(firstlist)
		firstlevel = firstLevel(o,lc,cp,h,l,b1,a1,v,a)
		return firstlevel
	def getsecbidinfo(self):
		content = self.getcontent()
		bidlist = content.split(',')[11:21]
		bidv = map(int, bidlist[1::2])
		bid = map(float, bidlist[::2])
		return secBid(bidv, bid)
	def getsecaskinfo(self):
		content = self.getcontent()
		asklist = content.split(',')[11:21]
		askv = map(int, asklist[1::2])
		ask = map(float, asklist[::2])
		return secAsk(askv, ask)
	def getdate(self):
		content = self.getcontent()
		return content.split(',')[-3]
	def gettime(self):
		content = self.getcontent()
		return content.split(',')[-2]


if __name__ == '__main__':
	print stockInfo('sh601318').getsecaskinfo().askvolumn
	print stockInfo('sz000001').gettime()