# -*- coding: utf-8 -*-

import urllib2
from BeautifulSoup import *
from urlparse import urljoin
from sqlite3 import dbapi2 as sqlite
# from pysqlite2 import dbapi2 as sqlite

ignorewords = set(["the", "of", "to", "and", "a", "in", "is", "iGt"])

class crawler:
  def __init__(self, dbname):
    self.con = sqlite.connect(dbname)

  def __del__(self):
    self.con.close()

  def dbcommit(self):
    self.con.commit()

  # 항목번호를 얻는다. 항목이 존재하지 않는다면 새로 만들어서 해당 rowid 를 반환한다. 
  def getEntryID(self, table, field, value, creatnew=True):
    cur = self.con.execute(
      "select rowid from %s where %s = '%s'" % (table, field, value))
    res = cur.fetchone()
    if res == None:
      cur = self.con.execute(
        "insert into %s (%s) values ('%s')" % (table, field, value))
      return cur.lastrowid
    else:
      return res[0]

  def addToIndex(self, url, soup):
    if self.isIndexed(url): return

    print "Indexing %s" % url

    text = self.getTextOnly(soup)
    words = self.seprateWords(text)

    urlid = self.getEntryID("urllist", "url", url)

    for i in range(len(words)):
      word = words[i]
      if word in ignorewords: continue
      wordid = self.getEntryID("wordlist", "word", word)
      self.con.execute("insert into wordlocation(urlid, wordid, location) \
        values (%d, %d, %d)" % (urlid, wordid, i))

  # 텍스트를 추출한다.
  def getTextOnly(self, soup):
    v = soup.string 
    # 하위 노드들이 존재한다면..
    if v == None:
      c = soup.contents
      resultText = ""
      for t in c:
        subtext = self.getTextOnly(t)
        resultText += subtext + "\n"
      return resultText
    else:
      return v.strip()

  # 단어들을 분리한다.
  def seprateWords(self, text):
    splitter = re.compile("\\W*")
    return [s.lower() for s in splitter.split(text) if s != ""]

  # 색인 & 크롤링이 되었는가? 
  def isIndexed(self, url):
    u = self.con.execute \
      ("select rowid from urllist where url = '%s'" % url).fetchone()
    if u != None:
      # 이미 크롤 되었는지 확인한다.
      v = self.con.execute(
        "select * from wordlocation where urlid = %d" % u[0]).fetchone()
      if v != None: return True
    return False

  # 두 페이지 간의 링크를 추가
  def addLinkRef(self, urlFrom, urlTo, linkText): 
    if urlFrom == urlTo: return 
    fromid = self.getEntryID("urllist", "url", urlFrom)
    toid = self.getEntryID("urllist", "url", urlTo)
    cur = self.con.execute(
      "insert into link(fromid, toid) values(%d, %d)" % (fromid, toid))
    linkid = cur.lastrowid
    words = self.seprateWords(linkText)
    for word in words:
      if word in ignorewords: continue
      wordid = self.getEntryID("wordlist", "word", word)
      self.con.execute(
        "insert into linkwords(wordid, linkid) values(%d, %d)" % (wordid, linkid))
  
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
        try:
          soup = BeautifulSoup(c.read())
        except:
          print "Could not read %s" % page
          continue
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


  # db 테이블들을 생성한다.  # 각 링크의 페이지랭크 점수를 계산한다. 
  def calculatePageRank(self, iter=20):
    # clear table
    self.con.execute("drop table if exists pagerank")
    self.con.execute("create table pagerank(urlid primary key, score)")
    
    # 모든 url 을 1 로 초기화 
    self.con.execute("insert into pagerank select rowid, 1.0 from urllist")
    self.dbcommit();
    
    for i in range(iter):
      print "Iteration %d" % i 
      for (urlid, ) in self.con.execute("select rowid from urllist"):
        # 초기 확률은 0.15로 고정
        pr = 0.15
        for (linker, ) in self.con.execute(
          "select distinct fromid from link where toid=%d" % urlid):
          linkingPR = self.con.execute(
            "select score from pagerank where urlid = %d" % linker).fetchone()[0]
          linkingCount = self.con.execute(
            "select count(*) from link where fromid = %d" % linker).fetchone()[0]
          pr += 0.85 * (linkingPR/linkingCount)
        self.con.execute(
          "update pagerank set score = %f where urlid = %d" %(pr, urlid))
      self.dbcommit()
          
            
    

  def createIndexTables(self):
    self.con.execute("create table urllist(url)")
    self.con.execute("create table wordlist(word)")
    self.con.execute("create table wordlocation(urlid, wordid, location)")
    self.con.execute("create table link(fromid integer, toid integer)")
    self.con.execute("create table linkwords(wordid, linkid)")
    self.con.execute("create index wordidx on wordlist(word)")
    self.con.execute("create index urlidx on urllist(url)")
    self.con.execute("create index wordurlidx on wordlocation(wordid)")
    self.con.execute("create index urltoidx on link(toid)")
    self.con.execute("create index urlfromidx on link(fromid)")
    self.dbcommit()

    


class searcher:
  def __init__(self, dbname):
    self.con = sqlite.connect(dbname)

  def __del__(self):
    self.con.close()

  # 쿼리에 매칭되는 결과와 wordid 반환한다. 
  def getMatchRows(self, q):
    fieldList = "w0.urlid"
    tableList = ""
    clauseList = ""
    wordids = []

    words = q.split(" ")
    tableNumber = 0

    for word in words:
      # 색인된 단어인지 찾는다.
      wordRow = self.con.execute(
        "select rowid from wordlist where word = '%s'" % word).fetchone()
      if wordRow != None:
        wordid = wordRow[0]
        wordids.append(wordid)
        if tableNumber > 0:
          tableList += ","
          clauseList += " and "
          clauseList += "w%d.urlid = w%d.urlid and " % (tableNumber - 1 , tableNumber)
        fieldList += ", w%d.location" % tableNumber
        tableList += "wordlocation w%d" % tableNumber
        clauseList += "w%d.wordid = %d" % (tableNumber, wordid)
        tableNumber += 1

    fullQuery = "select %s from %s where %s" % (fieldList, tableList, clauseList)
    cur = self.con.execute(fullQuery)
    rows = [row for row in cur]
    return rows, wordids

  # 가중평가된 점수를 가져온다. 
  def getScoredList(self, rows, wordids):
    totalScores = dict([(row[0], 0) for row in rows])

    weights = [
                (1.0, self.frequencyScore(rows))
                , (1.5, self.locationScore(rows))
                , (1.0, self.pagerankScore(rows)) 
                ]
    # weights = [(1.0, self.distanceScore(rows))]

    for (weight, scores) in weights:
      for url in totalScores:
        totalScores[url] += weight * scores[url]

    return totalScores

  # url 을 가져온다.
  def getUrlName(self, id):
    return self.con.execute(
      "select url from urllist where rowid = %d" % id).fetchone()[0]

  # 쿼리를 던진다.
  def query(self, q):
    rows, wordids = self.getMatchRows(q)
    scores = self.getScoredList(rows, wordids)
    rankedScores = sorted([(score, url) for (url, score) in scores.items()], reverse=1)
    for (score, urlid) in rankedScores[0:10]:
      print "%f\t%s" % (score, self.getUrlName(urlid))

  # 각 평가함수의 결과값을 정규화한다. [0, 1] 사이의 값을 반환한다. 
  # 결과 중 1이 제일 좋은 값이다.
  def normalizeScores(self, scores, smallIsBetter=0):
    vsmall = 0.000001 
    if smallIsBetter:
      minScore = min(scores.values())
      return dict([(url, float(minScore)/max(vsmall, score)) for (url, score) in scores.items()])
    else:
      maxScore = max(scores.values())
      if maxScore == 0: maxScore = vsmall
      return dict([(url, float(score)/maxScore) for (url, score) in scores.items()])

  # 빈도수로 평가한다.  
  # row[0] 은 url 이다. url 의 빈도수가 많다는 건, 검색한 단어들이 해당 문서에 많이 포함되어 있다는 것이다. 
  def frequencyScore(self, rows):
    counts = dict([(row[0], 0) for row in rows])
    for row in rows: counts[row[0]] += 1
    return self.normalizeScores(counts)

  # 각 단어들의 위치를 사용하여 점수를 게산한다. 
  def locationScore(self, rows):
    # 초기 점수는 임의의 큰수로 설정한다. 각 단어의 위치합은 아마 이보다는 작을 것이다.  
    locations = dict([(row[0], 1000000) for row in rows])
    for row in rows:
      loc = sum(row[1:])
      if loc < locations[row[0]]: locations[row[0]] = loc

    return self.normalizeScores(locations, smallIsBetter = 1)

  # 단어들 사이의 거리를 기반으로 한 점수 
  def distanceScore(self, rows):
    # 검색어가 한 단어라면 1을 반환한다.
    if (len(rows[0])) <= 2: return dict([(row[0], 1.0) for row in rows])

    minDist = dict([(row[0], 1000000) for row in rows])
    for row in rows:
      dist = sum([abs(row[i] - row[i-1]) for i in range(2, len(row))])
      if dist < minDist[row[0]]: minDist[row[0]] = dist 

    return self.normalizeScores(minDist, smallIsBetter = 1)
   
  # inbound link 를 기준으로 점수를 계산한다. 
  def inboundLinkScore(self, rows):
    uniqueUrls = set([row[0] for row in rows])
    inboundCount = dict([(url, self.con.execute(\
      "select count(*) from link where toid = %d" % url).fetchone()[0]) 
      for url in uniqueUrls])
    return self.normalizeScores(inboundCount)
    
  # pagerank 점수를 계산한다. 
  def pagerankScore(self, rows):
    pageranks = dict([(row[0], self.con.execute(
      "select score from pagerank where urlid = %d" % row[0]).fetchone()[0]) 
      for row in rows])
    maxScore = max(pageranks.values())
    normalizedScores = dict([(url, float(score)/maxScore) for (url, score) in pageranks.items()])
    return normalizedScores
  








    
