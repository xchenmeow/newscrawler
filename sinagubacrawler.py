# -*- coding: utf-8 -*

import urllib2
from bs4 import BeautifulSoup
import datetime
import csv
import sys
import os.path



## data structure
class Sent(object):
	def __init__(self, ticker, sent, time):
		self.ticker = ticker
		self.sent = sent
		self.time = time


## read url
def findTextTime():
	urlstr = 'http://finance.sina.com.cn/guba/ggjh/1.html'
	soup = BeautifulSoup(urllib2.urlopen(urlstr).read())
	rows = soup.find_all('div','listBlk')
	content = rows[0].find_all('a')
	time = rows[0].find_all('font')
	## structure
	# <div class='listBlk'><div ... ></div><ul ... >
	# <li><a href=... target='blank'>xxxxx</a><font...>...</font></li>
	# <li><a href=... target='blank'>xxxxx</a><font...>...</font></li>
	# </ul><div...></div></div>
	contenttext = []
	contenttime = []
	for row in content:
		try:
			if row['target'] == '_blank':
				contenttext.append(row.text)
		except KeyError:
			continue
	for row in time: 
		try:
			if row['color'] == '#6666cc':
				today = datetime.date.today()
				temptime = datetime.datetime(today.year, int(row.text[1:3]), int(row.text[4:6]), \
					int(row.text[8:10]), int(row.text[11:13]), 0)
				contenttime.append(temptime)
		except KeyError:
			continue
	return zip(contenttime, contenttext)

## finding ticker from text
# text format: name: content
# find the correspoding ticker to the name from a csv file
def findTicker(text):
	with open('000300cons.csv', 'r') as f:
		reader = csv.DictReader(f, delimiter=',')
		content = [(row['Exchange']+row['Ticker'], row['ConstituentName']) for row in reader]
		rawticker, name = zip(*content)
		ticker = [item.replace('Shenzhen','sz').replace('Shanghai','sh') for item in rawticker]
		codingtype = sys.getfilesystemencoding()
		name = [item.replace(u' '.encode(codingtype), '') for item in name]
		name = [item.replace(u'Ａ'.encode(codingtype), 'A') for item in name]
		newsticker = 0
		try:
			cname, content = text.encode(codingtype).split(u'：'.encode(codingtype), 1)
			try:
				newsticker = ticker[name.index(cname)]
			except ValueError:
				newsticker = 1
		except ValueError:
			newsticker = 0
		
		return newsticker



# if findTicker==0, dig in to see the whole passage
# return a list of ticker and correspoding sentiment score
def digIn(text):
	urlstr = 'http://finance.sina.com.cn/guba/ggjh/1.html'
	soup = BeautifulSoup(urllib2.urlopen(urlstr).read())
	texthtml = soup.find_all(target='_blank',text=text)
	href = texthtml[0]['href']
	newsoup = BeautifulSoup(urllib2.urlopen(href).read())
	passagetext = newsoup.find_all('div',attrs={'class':'ilt_p'})
	try:
		mentionedticker = [item['id'] for item in passagetext[0].find_all('span', attrs={'class':'showStock'})]
	except IndexError:
		mentionedticker = []
	## TODO
	# should filter out bad tickers in mentionedticker
	# e.g. bloomberg(BLG) says XXXXX. BLG is a bad ticker
	tickerlist = list(set([item.replace('stock_','') for item in mentionedticker]))
	## TODO
	# calculate sentiment score in each corrsponding paragraph for each ticker
	sent = [calSentimentScore(text)] * len(tickerlist)
	return zip(tickerlist, sent)




## calculating sentiment score of text
# sentimentdict.txt need to be enlarged
def calSentimentScore(text):
	codingtype = sys.getfilesystemencoding()
	try:
		cname, content = text.encode(codingtype).split(u'：'.encode(codingtype), 1)
	except ValueError:
		cname = 0
		content = text.encode(codingtype)
	afinnfile = open('sentimentdict.txt')
	scores = {}
	for line in afinnfile:
		term, score = line.split(",") # The file is csv
		scores[term] = int(score) # convert the score to an integer
	# print scores.items() # print every (term, score) pair in the dictionary
	afinnfile.close()
	score = 0
	for item in scores.keys():
		if item in content:
			score += scores[item] 
	# calculate frequency when returning 1
	return score

## find whether the news exists in the archive file
# given ticker and time as the news keys, read the last line of archived news
# with format ticker, sentiment score, time('%Y-%m-%d %H:%M:%S')
def isNewRecords(ticker, time):
	codingtype = sys.getfilesystemencoding()
	if not os.path.exists('archive.txt'):
		return True
	archive = open('archive.txt')
	lastitem = archive.readlines()[-1]
	archive.close()
	lastticker, lastsent, lasttime = lastitem.split(',')
	date_object = datetime.datetime.strptime(lasttime.strip(), '%Y-%m-%d %H:%M:%S')
	if time == date_object and ticker == lastticker:
		return False
	else:
		return True
	

def updateDataSet():
	codingtype = sys.getfilesystemencoding()
	time, text = zip(*findTextTime())
	ticker = []
	sentimentscore = []
	newstime = []
	for i in range(len(time)):
		if findTicker(text[i]) != 0  and findTicker(text[i]) != 1:
			ticker.append(findTicker(text[i]))
			sentimentscore.append(calSentimentScore(text[i]))
			newstime.append(time[i])
		else:
			try:
				innerticker, innersent = zip(*digIn(text[i]))
			except ValueError:
				innerticker = []
				innersent = []
			for item in innerticker:
				ticker.append(item)
			for item in innersent:
				sentimentscore.append(item)
			for j in range(len(innerticker)):
				newstime.append(time[i])
			## TODO
			# order (ticker, sent, time) by time
			# read from SQL
	if not os.path.exists('archive.txt'):
		with open('archive.txt', 'wb') as f:
			data = []
			for i in range(len(ticker)):
				data.append([ticker[i], ',', str(sentimentscore[i]), ',', newstime[i].strftime('%Y-%m-%d %H:%M:%S'), '\n'])
				data.reverse()
				# TODO
				# not reverse but order by time
				# write to SQL
			for i in range(len(ticker)):
				f.writelines(data[i])
	else:
		if not isNewRecords(ticker[-1], newstime[-1]):
			print 'already up to date'
		else:
			with open('archive.txt', 'a+b') as f:  
				lasttime = f.readlines()[-1].split(',')[2]
				lasttime_object = datetime.datetime.strptime(lasttime.strip(), '%Y-%m-%d %H:%M:%S')
				## TODO
				# order????
				# write to SQL
				idx = newstime.index(lasttime_object)
				ticker1 = ticker[:idx]
				ticker1.reverse()
				sentimentscore1 = sentimentscore[:idx]
				sentimentscore1.reverse()
				time1 = newstime[:idx]
				time1.reverse()
				for i in range(len(ticker1)):
					f.writelines([ticker1[i], ',', str(sentimentscore1[i]), ',', time1[i].strftime('%Y-%m-%d %H:%M:%S'), '\n'])
	return 0

## searching keyword in the news
def searchKeyWord(keyword):
	codingtype = sys.getfilesystemencoding()
	time, text = zip(*findTextTime())
	ticker = []
	newstime = []
	sent = []
	for i in range(len(time)):
		if keyword in text[i]:
			ticker.append(findTicker(text[i]))
			newstime.append(time[i].strftime('%Y-%m-%d %H:%M:%S'))
			sent.append(calSentimentScore(text[i]))
			print text[i]
	return zip(ticker, newstime, sent)


# time, text = zip(*findTextTime())
# print text[0], time[0]
# print findTicker(u'万科A：看涨 (09月03日 17:00)')
# print calSentimentScore(u'万科A：看涨 (09月03日 17:00)')
# print isNewRecords('000002', datetime.datetime(2014,9,3,17,0,0))
# print digIn(u'两市普涨　机构游资亿元买入唐山港')

# print findTicker(text[0])
# print calSentimentScore(text[0])
# print isNewRecords(findTicker(text[0]), time[0])
# if findTicker(text[0]) == 0 or findTicker(text[0]) == 1:
# 	print digIn(text[0])
updateDataSet()
# TODO:
# write to csv(every day) with format \
# ticker(append if new), sentiment score+previous score today
# previous sentiment scores(average of previous n days) are stored in another csv(or sql)
# parse news every minute to accumulate data(append if new according to the time released)



