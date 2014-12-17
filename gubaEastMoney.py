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
	'''guba(unicode), time(timeobject), title(unicode)
	aut(unicode), href(string)'''
	def __init__(self, guba, time, title, aut, href):
		# self.clk = clk
		# self.rev = rev
		self.guba = guba
		self.time = time
		self.title = title
		self.aut = aut
		self.href = href
	def __eq__(self, other):
		codingtype = sys.getfilesystemencoding()
		eq1 = (self.guba.encode(codingtype) == other.guba.encode(codingtype))
		eq2 = ((self.time - other.time).total_seconds < 1)
		eq3 = (self.title.encode(codingtype) == other.title.encode(codingtype))
		eq4 = (self.aut.encode(codingtype) == other.aut.encode(codingtype))
		eq5 = (self.href == other.href)
		return all([eq1, eq2, eq3, eq4, eq5])


class ClkRev(object):
	'''clk(int), rev(int), lasttime(datetime.datetime), href(string)--FORIEGNKEY'''
	def __init__(self, clk, rev,href, lasttime):
		self.clk = clk
		self.rev = rev
		self.href = href
		self.lasttime = lasttime
	def __eq__(self, other):
		codingtype = sys.getfilesystemencoding()
		eq1 = (self.clk == other.clk)
		eq2 = (self.rev == other.rev)
		eq3 = (self.href == other.href)
		eq4 = ((self.lasttime - other.lasttime).total_seconds < 1)
		return all([eq1, eq2, eq3, eq4])

def FindPostInfo():
	'''findPostInfo returns clk, rev, guba, time, aut, title and href of a post'''
	codingtype = sys.getfilesystemencoding()
	postInfo = []
	clkrev = []
	baseurlstr = 'http://guba.eastmoney.com/'
	for i in range(1,3501):
		urlstr = baseurlstr + 'default_' + str(i) + '.html'
		print i
		soup = BeautifulSoup(urllib2.urlopen(urlstr).read())
		row = soup.find('li','first')
		while row != None:
			clk = int(row.find_all('cite')[0].string)
			rev = int(row.find_all('cite')[1].string)
			guba = unicode(row.find('a', 'balink').string)
			title = unicode(row.find('a', 'note').string)
			aut = unicode(row.find('cite', 'aut').string)
			try:
				time = ParseTime(row.find('cite', 'date').string)
			except ValueError:
				print row.find('cite', 'date').string
				time = datetime.datetime(2014,12,9,0,0,0)
			lasttime = ParseTime(row.find('cite', 'last').string)
			href = baseurlstr + row.find('a', 'note')['href']
			postInfo.append(PostInfo(guba, time, title, aut, href))
			clkrev.append(ClkRev(clk, rev, href, lasttime))
			row = row.next_sibling.next_sibling
	return (postInfo, clkrev)

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

def IsNewRecord(postInfo, clkrev, oldpostinfo, oldclkrev):
	"""take a postInfo to see if it is a new or updated record in database
	0 for old, 1 for new, 2 for updated"""
	codingtype = sys.getfilesystemencoding()
	if not os.path.exists('EastMoneyArchive.csv'):
		return 1 
	if postInfo.href != clkrev.href:
		return -1
	# df = pd.read_csv('EastMoneyArchive.csv')
	# df2 = pd.read_csv('EastMoneyClkRev.csv')
	df = oldpostinfo
	df2 = oldclkrev
	olditem = df[df['href']==postInfo.href]
	a1 = df2[df2['href']==clkrev.href]
	a2 = df2[df2['lasttime']==clkrev.lasttime]
	oldclkrev = pd.merge(a1, a2)
	if not olditem.empty:
		if not oldclkrev.empty:
			return 0
		else:
			return 2
	else:
		return 1


def IsNewDF(postInfoList, clkrevList):
	'''newdf diff olddf'''
	postinfodict = {'guba':[],'title':[],'time':[],'aut':[],'href':[]}
	clkrevdict = {'clk':[], 'rev':[], 'href':[], 'lasttime':[]}
	for postinfo in postInfoList:
		postinfodict['guba'].append(postinfo.guba.encode(codingtype))
		postinfodict['title'].append(postinfo.title.encode(codingtype))
		postinfodict['time'].append(postinfo.time)
		postinfodict['aut'].append(postinfo.aut.encode(codingtype))
		postinfodict['href'].append(postinfo.href)
	for clkrev in clkrevList:
		clkrevdict['clk'].append(clkrev.clk)
		clkrevdict['rev'].append(clkrev.rev)
		clkrevdict['lasttime'].append(clkrev.lasttime)
		clkrevdict['href'].append(clkrev.href)
	df = pd.DataFrame(postinfodict)
	df2 = pd.DataFrame(clkrevdict)
	olddf = pd.read_csv('EastMoneyArchive.csv')
	olddf2 = pd.read_csv('EastMoneyClkRev.csv') 
	intersectionkey = list(set(list(df['href'])).intersection(list(olddf['href'])))
	# intersectionkey = [filter(lambda x: x in list(df['href']), sublist) for sublist in list(olddf['href'])]
	# intersectiontime = list(set(list(df2['lasttime'])).intersection(list(olddf2['lasttime'])))
	for key in intersectionkey:
		newdf = df.drop(df.index[df['href']==key])
	# for key2 in intersectiontime:
	# 	a1 = df2[df2['href']==key]
	# 	a2 = df2[df2['lasttime']==key2]
	# 	oldclkrev = pd.merge(a1, a2)
	# 	newdf2 = df2.drop(oldclkrev)
	newdf2 = df2
	newdf = newdf.drop_duplicates()
	newdf2 = newdf2.drop_duplicates()
	return (newdf, newdf2)



def UpdateDataSet(postInfoList, clkrevList):
	'''postInfoList is a list of PostInfo, if the PostInfo is a new record, append it to csv;
	if it is updated, append to clkrev'''
	if len(postInfoList) != len(clkrevList):
		return -1
	f = 'EastMoneyArchive.csv'
	f2 = 'EastMoneyClkRev.csv'
	
	newPostInfoList = []
	newclkrevList = []
	if not os.path.exists(f):
		newPostInfoList = postInfoList
		newclkrevList = clkrevList
		postinfodict = {'guba':[],'title':[],'time':[],'aut':[],'href':[]}
		clkrevdict = {'clk':[], 'rev':[], 'href':[], 'lasttime':[]}
		for postinfo in newPostInfoList:
			postinfodict['guba'].append(postinfo.guba.encode(codingtype))
			postinfodict['title'].append(postinfo.title.encode(codingtype))
		 	postinfodict['time'].append(postinfo.time)
		 	postinfodict['aut'].append(postinfo.aut.encode(codingtype))
		 	postinfodict['href'].append(postinfo.href)
		for clkrev in newclkrevList:
		 	clkrevdict['clk'].append(clkrev.clk)
		 	clkrevdict['rev'].append(clkrev.rev)
		 	clkrevdict['lasttime'].append(clkrev.lasttime)
		 	clkrevdict['href'].append(clkrev.href)
		df = pd.DataFrame(postinfodict)
		df2 = pd.DataFrame(clkrevdict)
		df = df.drop_duplicates()
		df2 = df2.drop_duplicates()
	else:
		df = pd.read_csv('EastMoneyArchive.csv')
		df2 = pd.read_csv('EastMoneyClkRev.csv')
		(df,df2) = IsNewDF(postInfoList, clkrevList)
		# newdf = pd.dataFrame(postinfoList)
		# newdf2 = pd.dataFrame(clkrevList)
		# for (postinfo, clkrev) in zip(postInfoList, clkrevList):
		# 	if IsNewRecord(postinfo, clkrev,df,df2) == 0:
		# 		continue
		# 	elif IsNewRecord(postinfo, clkrev,df,df2) == 1:
		# 		newPostInfoList.append(postinfo)
		# 		newclkrevList.append(clkrev)
		# 	elif IsNewRecord(postinfo, clkrev,df,df2) == 2:
		# 		newclkrevList.append(clkrev)
	# postinfodict = {'guba':[],'title':[],'time':[],'aut':[],'href':[]}
	# clkrevdict = {'clk':[], 'rev':[], 'href':[], 'lasttime':[]}
	# for postinfo in newPostInfoList:
	# 	postinfodict['guba'].append(postinfo.guba.encode(codingtype))
	# 	postinfodict['title'].append(postinfo.title.encode(codingtype))
	# 	postinfodict['time'].append(postinfo.time)
	# 	postinfodict['aut'].append(postinfo.aut.encode(codingtype))
	# 	postinfodict['href'].append(postinfo.href)
	# for clkrev in newclkrevList:
	# 	clkrevdict['clk'].append(clkrev.clk)
	# 	clkrevdict['rev'].append(clkrev.rev)
	# 	clkrevdict['lasttime'].append(clkrev.lasttime)
	# 	clkrevdict['href'].append(clkrev.href)
	# df = pd.DataFrame(postinfodict)
	# df2 = pd.DataFrame(clkrevdict)
	if not os.path.exists(f):  
		with open(f, 'w') as archive:
			df.to_csv(archive, header=True, index=False)
		with open(f2, 'w') as archive2:
			df2.to_csv(archive2, header=True, index=False)
	else:
		with open(f, 'a') as archive: 
			df.to_csv(archive, header=False, index=False)
		with open(f2, 'a') as archive2: 
			df2.to_csv(archive2, header=False, index=False)



codingtype = sys.getfilesystemencoding()
(p,r) = FindPostInfo()
# print len(b)
# a = b[6]
# b = [PostInfo(12,3,u'上证指数吧', datetime.date.today(), u'最珍贵是大盘回探那一笑 接下来的选股思路揭秘', 'abc', 'http://google.com')]
# b = [PostInfo(2241,11,'股市实战吧',datetime.datetime(2014,11,21,10,0,0),'国务院发布能源规划，核电目标装机未下调','恋股人',"http://guba.eastmoney.com//news,gssz,131248360.html")]
a1 = p[0]
a2 = r[0]
# print a.clk, a.rev, a.aut.encode(codingtype), a.href, a.title.encode(codingtype), a.guba.encode(codingtype), a.time
# print ParseText(a.title)
# print FindTicker(a.guba)
UpdateDataSet(p,r)
# print FindTicker(u'上证指数吧')
# print ParseTime(u'09-24 11:44')
# print IsNewRecord(a1,a2)