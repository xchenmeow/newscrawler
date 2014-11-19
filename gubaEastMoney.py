# -*- coding: utf-8 -*

import urllib2
from bs4 import BeautifulSoup
import datetime
import csv
import sys
import os.path
import scseg


class PostInfo(object):
	def __init__(self, clk, rev, guba, time, title, aut, href):
		self.clk = clk
		self.rev = rev
		self.guba = guba
		self.time = time
		self.title = title
		self.aut = aut
		self.href = href


def FindPostInfo():
	'''findPostInfo returns clk, rev, guba, time, aut, title and href of a post'''
	postInfo = []
	baseurlstr = 'http://guba.eastmoney.com/'
	for i in range(1,16):
		urlstr = baseurlstr + 'default_' + str(i) + '.html'
		print urlstr
		soup = BeautifulSoup(urllib2.urlopen(urlstr).read())
		row = soup.find('li','first')
		while row != None:
			clk = row.find_all('cite')[0].string
			rev = row.find_all('cite')[1].string
			guba = row.find('a', 'balink').string
			title = row.find('a', 'note').string
			aut = row.find('cite', 'aut').string
			time = row.find('cite', 'date').string
			href = baseurlstr + row.find('a', 'note')['href']
			postInfo.append(PostInfo(clk, rev, guba, time, title, aut, href))
			row = row.next_sibling.next_sibling
	return postInfo

def ParseText(text):
	'''parsetext returns a sentiment score of text(unicode)
	sentiment score calculated from gubadict.txt'''
	codingtype = sys.getfilesystemencoding()
	seg_list = list(scseg.seg_keywords(text))
	afinnfile = open('gubadict.txt') 
	scores = {}
	for line in afinnfile:
		term, score = line.split(",") # The file is csv
		scores[term] = int(score) # convert the score to an integer
	# print scores.items() # print every (term, score) pair in the dictionary
	afinnfile.close()
	totalscore = 0
	for item in seg_list:
		try:
			totalscore += scores[item.encode(codingtype)]
		except KeyError:
			continue
	return totalscore

def FindTicker(guba):
	"""turn guba into ticker.
	if cannot find it in A share list then return 0"""
	codingtype = sys.getfilesystemencoding()
	guba = guba.replace(u'吧', '')
	with open('AShareTickerList.csv', 'r') as f:
		reader = csv.DictReader(f, delimiter=',')
		content = [(row['Ticker'], row['Name']) for row in reader]
		ticker, name = zip(*content)
		# ticker = [item.replace('Shenzhen','sz').replace('Shanghai','sh') for item in rawticker]
		codingtype = sys.getfilesystemencoding()
		name = [item.replace(u' '.encode(codingtype), '') for item in name]
		name = [item.replace(u'Ａ'.encode(codingtype), 'A') for item in name]
		try:
			newsticker = ticker[name.index(guba.encode(codingtype))]
			if newsticker[0] == '0' or newsticker[0] == '3':
				newsticker = 'sz' + newsticker
			elif newsticker[0] == '6':
				newsticker = 'sh' + newsticker
		except ValueError:
			if guba == u'上证指数':
				newsticker = 'sh000001'
			elif guba == u'深证成指':
				newsticker = 'sz399106'
			elif guba == u'沪深300':
				newsticker = '000300'
			else:
				newsticker = 0
		
		return newsticker

def ParseTime(time):
	"""turn a time string into a time object in python"""
	codingtype = sys.getfilesystemencoding()
	time = str(datetime.date.today().year) + '-' + time
	timeobj = datetime.datetime.strptime(time.encode(codingtype).strip(), '%Y-%m-%d %H:%M')
	return timeobj

def IsNewRecord(postInfo):
	"""take a postInfo to see if it is a new or updated record in database"""
	# key: title, aut???
	pass

def UpdateDataSet():
	pass



codingtype = sys.getfilesystemencoding()
b = FindPostInfo()
print len(b)
a = b[6]
# a = (u'上证指数吧',u'09-24 11:44',u'最珍贵是大盘回探那一笑 接下来的选股思路揭秘')
# guba = a[0].encode(codingtype)
# time = a[1].encode(codingtype)
# title = a[2].encode(codingtype)
# print guba, time, title
print a.clk, a.rev, a.aut.encode(codingtype), a.href, a.title.encode(codingtype), a.guba.encode(codingtype)
print ParseText(a.title)
print FindTicker(a.guba)
print ParseTime(a.time)
# print FindTicker(u'上证指数吧')
# print ParseTime(u'09-24 11:44')
