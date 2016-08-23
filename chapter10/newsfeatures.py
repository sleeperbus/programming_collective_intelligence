# -*- coding: utf-8 -*-
import feedparser
import re

feedlist = ['http://feeds.reuters.com/reuters/topNews',
            'http://feeds.reuters.com/Reuters/domesticNews',
            'http://feeds.reuters.com/Reuters/worldNews',
            'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305',
            'http://hosted2.ap.org/atom/APDEFAULT/386c25518f464186bf7a2ac026580ce7',
            'http://hosted2.ap.org/atom/APDEFAULT/cae69a7523db45408eeb2b3a98c0c9c5',
            'http://hosted2.ap.org/atom/APDEFAULT/89ae8247abe8493fae24405546e9a1aa',
            'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
            'http://www.nytimes.com/services/xml/rss/nyt/InternationalHome.xml',
            'https://news.google.com/?output=rss',
            'http://www.salon.com/rss',
            'http://feeds.foxnews.com/foxnews/most-popular',
            'http://rss.cnn.com/rss/edition.rss',
            'http://rss.cnn.com/rss/edition_world.rss',
            'http://rss.cnn.com/rss/edition_us.rss',]

def stripHTML(h):
  p = ''
  s = 0
  for c in h:
    if c == '<': s = 1
    elif c == '>':
      s = 0
      p += ' '
    elif s == 0: p += c
  return p

def separatewords(text):
  splitter = re.compile('\\W*')
  return [s.lower() for s in splitter.split(text) if len(s) > 3]


def getarticlewords():
  allwords = {}
  articlewords = []
  articletitles = []
  ec = 0

  for feed in feedlist:
    print('%s parsing ...' % feed)
    f = feedparser.parse(feed) 
    for e in f.entries:
      print('%title: %s ...' % e.title)
      if e.title in articletitles: continue
      txt = e.title.encode('utf8') + stripHTML(e.description.encode('utf8'))
      words = separatewords(txt)
      articlewords.append({})
      articletitles.append(e.title)

      for word in words: 
        allwords.setdefault(word, 0)
        allwords[word] += 1
        articlewords[ec].setdefault(word, 0)
        articlewords[ec][word] += 1
      ec += 1
  return allwords, articlewords, articletitles


def makematrix(allw, articlew):
  wordvec = []

  for w, c in allw.items():
    if c > 3 and c < len(articlew) * 0.6:
      wordvec.append(w)

  l1 = [[(word in f and f[word] or 0) for word in wordvec] for f in articlew]
  return l1, wordvec
