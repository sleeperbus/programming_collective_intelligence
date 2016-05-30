# -*- coding: utf-8 -*-

import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite

class crawler:
  def __init__(self, dbname):
    pass

  def __del__(self):
    pass

  def dbcommit(self):
    pass

  # 항목번호를 얻는다. 
  def getEntryID(self, table, field, value, creatnew=True):
    return None 

  def addToIndex(self, url, soup):
    print "Indexing %s" % url

  # 텍스트를 추출한다.
  def getTextOnly(self, soup):
    return None

  # 단어들을 분리한다.
  def seprateWords(self, text):
    return None

  # 색인한 적이 있는가?
  def isIndexed(self, url):
    return False

  # 두 페이지 간의 링크를 추가
  def addLinkRef(self, urlFrom, urlTo, linkText):
    pass

  # 페이지 목록을 색인함
  def crawl(self, pages, depth=2):
    for i in range(depth):
      newpages = set()
      for page in pages:
        try:
          c = urllib2.urlopen(page)
        except:
          print "Could not open %s" % page 
          continue
        soup = BeautifulSoup(c.read())
        self.addToIndex(page, soup)

        links = soup("a")
        for link in links:
          if ("href" in dict(link.attrs)):
            url = urljoin(page, link["href"])
            if url.find("'") != -1: continue
            # location 부분을 제거함 
            url = url.split("#")[0]
            if url[0:4] == "http" and not self.isIndexed(url):
              newpages.add(url)
            linkText = self.getTextOnly(link)
            self.addLinkRef(page, url, linkText)
        self.dbcommit()
      pages = newpages


  # db 테이블들을 생성한다.
  def createIndexTables(self):
    pass


    
