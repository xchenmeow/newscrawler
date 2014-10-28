

import urllib2
from bs4 import BeautifulSoup
import datetime
import csv
import sys
import os.path


def findTimeText():
	urlstr = 'http://www.marketwatch.com/newsviewer?link=MW_Nav_NV'
	soup = BeautifulSoup(urllib2.urlopen(urlstr).read())
	rowsexp = soup.find_all('li','expandable')
	contentexp = [item.find('a').string for item in rowsexp]
	timeexp = [item['timestamp'] for item in rowsexp]
	## structure_expandable
	# <li id=xxxx timestamp=xxxx class="expandable">
	# <div class="nv-type-cont"><span class="nv-time">2:17a</span></div><div class="nv-text-cont"><h4>	
	# <a class="read-more" href=xxxx target="_blank">xxxxtitlexxxx</a>
	# </h4></div><div style="clear:both;"></div><div class="nv-details"><div>
	# <span>By MarketWatch.com</span><span>xxxxcontentxxxx</span></div>
	# <p class="abs">xxxx<a class="read-more" rel="nofollow" href=xxxx target="_blank">Full Story</a></p></div></li>
	rows = soup.find_all('div', 'nv-type-cont')
	content = [item.find('h4').string for item in rows]
	## structure_unexpandable
	# <li id=xxxx timestamp=xxtimexx><div class="nv-type-cont"><span class="nv-time">9/10</span></div>						
	# <div class="nv-text-cont"><h4>xxxxtitlexxxx</h4></div>
	# <div style="clear:both;"></div><div class="nv-details"></div></li>
	print len(contentexp), len(content)	


findTimeText()