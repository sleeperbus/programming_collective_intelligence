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






























  