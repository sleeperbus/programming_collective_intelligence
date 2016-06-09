# -*- coding: utf-8 -*-

from math import tanh
from sqlite3 import dbapi2 as sqlite 

class searchnet:
  def __init__(self, dbname):
    self.con = sqlite.connect(dbname)

  def __del__(self):
    self.con.close()

  # 테이블을 만든다.
  def makeTables(self):
    self.con.execute("create table hiddennode(create_key)")
    self.con.execute("create table wordhidden(fromid, toid, strength)")
    self.con.execute("create table hiddenurl(fromid, toid, strength)")
    self.con.commit()

  # 연결강도(가중치)를 가져온다. 
  def getStrength(self, fromid, toid, layer):
    if layer == 0: table = "wordhidden"
    else: table = "hiddenurl"
    res = self.con.execute(
      "select strength from %s where fromid = %d and toid = %d" % 
      (table, fromid, toid)).fetchone()
    if res == None:
      if layer == 0: return -0.2
      if layer == 1: return 0
    return res[0]

  # 가중치를 설정한다.
  def setStrength(self, fromid, toid, layer, strength):
    if layer == 0: table = "wordhidden"
    else: table = "hiddenurl"
    res = self.con.execute(
      "select rowid from %s where fromid = %d and toid = %d" % 
      (table, fromid, toid)).fetchone()
    if res == None:
      self.con.execute(
        "insert into %s(fromid, toid, strength) values (%d, %d, %f)" % 
        (table, fromid, toid, strength))
    else: 
      rowid = res[0]
      self.con.execute(
        "update %s set strength = %f where rowid = %d" % (table, strength, rowid))

  # hidden node 를 생성한다. hiddennode 의 형태는 단어_단어 이다. seoul_newyork 이런 식...
  def generateHiddenNode(self, wordids, urls):
    if len(wordids) > 3: return None
    createkey = "_".join(sorted([str(wi) for wi in wordids]))
    res = self.con.execute(
      "select rowid from hiddennode where create_key = '%s'" % createkey).fetchone()
    if res == None:
      cur = self.con.execute(
        "insert into hiddennode(create_key) values ('%s')" % createkey)
      hiddenid = cur.lastrowid
      # 기본값을 설정
      for wordid in wordids:
        self.setStrength(wordid, hiddenid, 0, 1.0/len(wordids))
      for urlid in urls:
        self.setStrength(hiddenid, urlid, 1, 0.1)
      self.con.commit()
      
  # 단어와 URL 에 연결된 hidden unit 을 반환한다.
  def getAllHiddenIDs(self, wordids, urlids):
    l1 = {}
    for wordid in wordids:
      cur = self.con.execute(
        "select toid from wordhidden where fromid = %d" % wordid)
      for row in cur: l1[row[0]] = 1
    for urlid in urlids:
      cur = self.con.execute(
        "select fromid from hiddenurl where toid = %d" % urlid)
      for row in cur: l1[row[0]] = 1
    return l1.keys()
  
  # 클래스 내용을 설정  
  def setupNetwork(self, wordids, urlids):
    self.wordids = wordids
    self.urlids = urlids
    self.hiddenids = self.getAllHiddenIDs(wordids, urlids)
    
    self.ai = [1.0] * len(self.wordids) 
    self.ah = [1.0] * len(self.hiddenids)
    self.ao = [1.0] * len(self.urlids) 
    
    self.wi = [[self.getStrength(wordid, hiddenid, 0) 
      for hiddenid in self.hiddenids] 
      for wordid in self.wordids]
    self.wo = [[self.getStrength(hiddenid, urlid, 1) 
      for urlid in self.urlids] 
      for hiddenid in self.hiddenids]
    
  # forward prop 로 output layer 의 결과를 계산한다.  
  def feedForward(self):
    # input layer 의 값은 1 
    for i in range(len(self.wordids)): self.ai[i] = 1
    
    # hidden layer 의 값은 input layer * weight 
    for j in range(len(self.hiddenids)):
      sum = 0.0 
      for i in range(len(self.wordids)):
        sum = sum + self.ai[i] * self.wi[i][j]
      self.ah[j] = tanh(sum)
      
    # output layer 의 결과를 구한다. 
    for k in range(len(self.urlids)):
      sum = 0.0 
      for j in range(len(self.hiddenids)):
        sum = sum + self.ah[j] * self.wo[j][k]
      self.ao[k] = tanh(sum)
      
    return self.ao[:]
    
  def getResult(self, wordids, urlids):
    self.setupNetwork(wordids, urlids)
    return self.feedForward()
      
  
    






























  