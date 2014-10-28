# -*- coding: utf-8 -*-
"""
Created on Tue Jun 10 16:29:39 2014

@author: zhangxf
"""

import urllib, urllib2,bs4, re, string, Tkinter
BASEURL='http://www.cninfo.com.cn'
BASEURL_SEARCH='http://www.cninfo.com.cn/search/search.jsp'



def gui_init():
    def do_work():
        print startdate_str.get()
        print enddate_str.get()
        print code_str.get()
        
        codes=code_str.get().split(',')
        for code in codes:
            np=getnotice(startdate_str.get(), enddate_str.get(),code )
            print np['title']
            for t in np['title']:
                text1.insert(Tkinter.INSERT, t+'\n')
        frame2.update()
    def get_list():
        try:
            f=open('d:/work/list.txt', 'r')
            a=f.readline()
            print a
            f.close()
        except:
            a=''            
        return a
        
    top=Tkinter.Tk()
    frame1=Tkinter.Frame(top,bd=1, relief= Tkinter.GROOVE)
    frame2=Tkinter.Frame(top,bd=1, relief= Tkinter.GROOVE)
    label1=Tkinter.Label(frame1, text='startdate')
    startdate_str=Tkinter.StringVar(frame1,'2013-12-31')
    entry1=Tkinter.Entry(frame1,textvariable=startdate_str)
    label2=Tkinter.Label(frame1, text='enddate')
    enddate_str=Tkinter.StringVar(frame1,'2013-12-31')
    entry2=Tkinter.Entry(frame1,textvariable=enddate_str)
    label3=Tkinter.Label(frame1, text='Code')
    code_str=Tkinter.StringVar(frame1,get_list())
    entry3=Tkinter.Entry(frame1, textvariable=code_str)
    label4=Tkinter.Label(frame1, text='Output')
    text1 =Tkinter.Text(frame2)
    buttom1=Tkinter.Button(frame1,text='Fetch Notice From www.cninfo.com.cn', command = do_work )

    label1.pack(fill=Tkinter.BOTH)
    entry1.pack(fill=Tkinter.BOTH)
    label2.pack(fill=Tkinter.BOTH)
    entry2.pack(fill=Tkinter.BOTH)
    label3.pack(fill=Tkinter.BOTH)
    entry3.pack(fill=Tkinter.BOTH)
    label4.pack(fill=Tkinter.BOTH)
    buttom1.pack(fill=Tkinter.BOTH)
    text1.pack(fill=Tkinter.BOTH)
    frame1.pack(side=Tkinter.LEFT,fill=Tkinter.BOTH)
    frame2.pack(side=Tkinter.RIGHT,fill=Tkinter.BOTH)    
    Tkinter.mainloop()



def getnotice(startTime='2014-06-30', endTime='2014-06-30', stockCode=''):
    postdata = {'endTime': '2014-06-30',
            'keyword': '',
            'marketType': '',
            'noticeType': '',
            'orderby': 'date11',
            'pageNo': 1,
            'startTime': '2014-06-30',
            'stockCode':''
        }
    postdata['endTime']=endTime
    postdata['startTime']=startTime
    postdata['stockCode']=stockCode
    curpg=1
    pgnum=999
    notice_parsed={'title':[], 'link':[]} 
    while curpg<=pgnum:
        postdata['pageNo']=curpg
        req=urllib2.Request(BASEURL_SEARCH, urllib.urlencode(postdata))
        resp=urllib2.urlopen(req)
        raw_html=resp.readlines()
        bs_obj=bs4.BeautifulSoup('\n'.join(raw_html).decode('gbk'))
        try:
            pgnum=max(string.atoi(t.contents[0]) for t in bs_obj.find_all('a', style="cursor:pointer;"))
        except:
            pgnum=1
            
        _np=bs_obj.find_all('a', target='new')
        for _tmp in _np:
            notice_parsed['title'].append(_tmp.text)
            notice_parsed['link'].append(_tmp.attrs['href'])   
            print _tmp.text
        curpg +=1
    return notice_parsed

    
if __name__ =='__main__':
    gui_init()
