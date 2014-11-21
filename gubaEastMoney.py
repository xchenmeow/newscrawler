# -*- coding: utf-8 -*

import urllib2
from bs4 import BeautifulSoup
import datetime
import csv
import sys
import os.path
import scseg
import pandas as pd

class PostInfo(object):
	'''clk(int), rev(int), guba(unicode), time(timeobject), title(unicode)
	aut(unicode), href(string)'''
	def __init__(self, clk, rev, guba, time, title, aut, href):
		self.clk = clk
		self.rev = rev
		self.guba = guba
		self.time = time
		self.title = title
		self.aut = aut
		self.href = href
	def __eq__(self, other):
		codingtype = sys.getfilesystemencoding()
		eq1 = self.clk == other.clk
		eq2 = self.rev == other.rev
		eq3 = self.guba.encode(codingtype) == other.guba.encode(codingtype)
		eq4 = self.time == other.time
		eq5 = self.title.encode(codingtype) == other.title.encode(codingtype)
		eq6 = self.aut.encode(codingtype) == other.aut.encode(codingtype)
		eq7 = self.href == other.href
		return all([eq1, eq2, eq3, eq4, eq5, eq6, eq7])


def FindPostInfo():
	'''findPostInfo returns clk, rev, guba, time, aut, title and href of a post'''
	codingtype = sys.getfilesystemencoding()
	postInfo = []
	baseurlstr = 'http://guba.eastmoney.com/'
	for i in range(1,16):
		urlstr = baseurlstr + 'default_' + str(i) + '.html'
		print urlstr
		soup = BeautifulSoup(urllib2.urlopen(urlstr).read())
		row = soup.find('li','first')
		while row != None:
			clk = int(row.find_all('cite')[0].string)
			rev = int(row.find_all('cite')[1].string)
			guba = unicode(row.find('a', 'balink').string)
			title = unicode(row.find('a', 'note').string)
			aut = unicode(row.find('cite', 'aut').string)
			time = ParseTime(row.find('cite', 'date').string)
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
	"""turn guba(unicode) into ticker.
	if cannot find it in A share list then return 0"""
	codingtype = sys.getfilesystemencoding()
	guba = guba.replace(u'吧', '')
	with open('AShareTickerList.csv', 'r') as f:
		reader = csv.DictReader(f, delimiter=',')
		content = [(row['Ticker'], row['Name']) for row in reader]
		ticker, name = zip(*content)
		# ticker = [item.replace('Shenzhen','sz').replace('Shanghai','sh') for item in rawticker]
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
	timey = str(datetime.date.today().year) + '-' + time
	timeobj = datetime.datetime.strptime(timey.encode(codingtype).strip(), '%Y-%m-%d %H:%M')
	return timeobj

def IsNewRecord(postInfo):
	"""take a postInfo to see if it is a new or updated record in database
	0 for old, 1 for new, 2 for updated"""
	codingtype = sys.getfilesystemencoding()
	if not os.path.exists('EastMoneyArchive.csv'):
		return 1
	df = pd.read_csv('EastMoneyArchive.csv')
	olditem = df[df['title']==postInfo.title.encode(codingtype)]
	if olditem.empty:
		return 1
	clk = olditem['clk'].ix[0]
	rev = olditem['rev'].ix[0]
	guba = olditem['guba'].ix[0].decode(codingtype)
	ptime = olditem['time']
	# date_object = datetime.datetime.strptime(ptime.strip(), '%Y-%m-%d %H:%M:%S')
	title = olditem['title'].ix[0].decode(codingtype)
	aut = olditem['aut'].ix[0].decode(codingtype)
	href = olditem['href'].ix[0]
	lastPostInfo = PostInfo(clk, rev, guba, ptime, title, aut, href)
	if lastPostInfo == postInfo:
		return 0
	else:
		return 2

def UpdateDataSet(postInfoList):
	'''postInfoList is a list of PostInfo, if the PostInfo is a new record, append it to csv;
	if it is updated, change it'''
	## CHANGE IT???
	## CLK CHANGES ALL THE TIME
	## PUT CLK AND REV TIME SERIES IN ANOTHER CSV???(KEY: TITLE)???
	postinfodict = {'clk':[],'rev':[],'guba':[],'title':[],'time':[],'aut':[],'href':[]}
	for postinfo in postInfoList:
		postinfodict['clk'].append(postinfo.clk)
		postinfodict['rev'].append(postinfo.rev)
		postinfodict['guba'].append(postinfo.guba.encode(codingtype))
		postinfodict['title'].append(postinfo.title.encode(codingtype))
		# postinfodict['time'].append(datetime.time.strftime('%Y-%m-%d %H:%M:%S', postinfo.time))
		postinfodict['time'].append(postinfo.time)
		postinfodict['aut'].append(postinfo.aut.encode(codingtype))
		postinfodict['href'].append(postinfo.href)
	df = pd.DataFrame(postinfodict)
	f = 'EastMoneyArchive.csv'
	if not os.path.exists(f):
		df.to_csv(f, index=False)
	else:
		pass




codingtype = sys.getfilesystemencoding()
b = FindPostInfo()
# print len(b)
# a = b[6]
# b = [PostInfo(12,3,u'上证指数吧', datetime.date.today(), u'最珍贵是大盘回探那一笑 接下来的选股思路揭秘', 'abc', 'http://google.com')]
# b = [PostInfo(2241,11,'股市实战吧',datetime.datetime(2014,11,21,10,0,0),'国务院发布能源规划，核电目标装机未下调','恋股人',"http://guba.eastmoney.com//news,gssz,131248360.html")]
a = b[0]
# print a.clk, a.rev, a.aut.encode(codingtype), a.href, a.title.encode(codingtype), a.guba.encode(codingtype), a.time
# print ParseText(a.title)
# print FindTicker(a.guba)
UpdateDataSet(b)
# print FindTicker(u'上证指数吧')
# print ParseTime(u'09-24 11:44')
print IsNewRecord(a)