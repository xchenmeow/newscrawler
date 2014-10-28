# -*- coding: utf-8 -*

import sys
import urllib2
from bs4 import BeautifulSoup


urlstr = 'http://live.sina.com.cn/zt/f/v/finance/globalnews1'
soup = BeautifulSoup(urllib2.urlopen(urlstr).read())
rows = soup.find_all('p')
text = []
for row in rows:
	try:
		if row[u'class'] == ['bd_i_txt_c']:
			text.append(row.string)
	except KeyError:
		continue
print len(text)
# codingtype = sys.getfilesystemencoding()
# a = '啊'
# print a.decode('utf-8').encode(codingtype)