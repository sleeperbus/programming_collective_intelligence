# -*- coding: utf-8 -*-
import feedparser
import re
from numpy import *

feedlist = ['http://feeds.reuters.com/reuters/topNews',
            'http://feeds.reuters.com/Reuters/domesticNews',
            'http://feeds.reuters.com/Reuters/worldNews',
            'http://feeds.reuters.com/reuters/technologyNews',
            'http://hosted2.ap.org/atom/APDEFAULT/495d344a0d10421e9baa8ee77029cfbd',
            'http://hosted2.ap.org/atom/APDEFAULT/bbd825583c8542898e6fa7d440b9febc',
            'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305',
            'http://hosted2.ap.org/atom/APDEFAULT/386c25518f464186bf7a2ac026580ce7',
            'http://hosted2.ap.org/atom/APDEFAULT/cae69a7523db45408eeb2b3a98c0c9c5',
            'http://hosted2.ap.org/atom/APDEFAULT/89ae8247abe8493fae24405546e9a1aa',
            'http://www.nytimes.com/services/xml/rss/nyt/Health.xml',
            'http://feeds.nytimes.com/nyt/rss/Technology',
            'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
            'http://www.nytimes.com/services/xml/rss/nyt/InternationalHome.xml',
            'https://news.google.com/?output=rss',
            'http://www.salon.com/rss',
            'http://feeds.foxnews.com/foxnews/most-popular',
            'http://feeds.foxnews.com/foxnews/health',
            'http://feeds.foxnews.com/foxnews/tech',
            'http://rss.cnn.com/rss/edition_technology.rss',
            'http://rss.cnn.com/rss/cnn_latest.rss',
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
    f = feedparser.parse(feed) 
    for e in f.entries:
      try:
        if e.title in articletitles: continue
        txt = e.title.encode('utf8') + stripHTML(e.description.encode('utf8'))
        words = separatewords(txt)
        articlewords.append({})
        articletitles.append(e.title)
      except:
        continue

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
  	# 최소 등장 회수 
  	# 너무 많이 등장하는 단어들은 is, the 같은 단어일수 있으므로 제외
    if c > 3 and c < len(articlew) * 0.6:
      wordvec.append(w)

  l1 = [[(word in f and f[word] or 0) for word in wordvec] for f in articlew]
  return l1, wordvec

def showfeatures(w, h, titles, wordvec, out='features.txt'):
  outfile = file(out, 'w')
  pc, wc = shape(h)
  toppatterns = [[] for i in range(len(titles))]
  patternnames = []

  # Loop over all the features
  for i in range(pc):
    slist = []
    # Create a list of words and their weights
    for j in range(wc):
      slist.append((h[i,j], wordvec[j]))
    # Reverse sort the word list
    slist.sort()
    slist.reverse()

    # Print the first six elements
    n = [s[1] for s in slist[0:6]]
    outfile.write(str(n)+'\n')
    patternnames.append(n)

    # Create a list of articles for this feature
    flist = []
    for j in range(len(titles)):
      # Add the article with its weight
      flist.append((w[j, i], titles[j]))
      toppatterns[j].append((w[j,i], i, titles[j]))

    # Reverse sort the list
    flist.sort()
    flist.reverse()

    # Show the top 3 articles
    for f in flist[0:3]:
      outfile.write(str(f)+'\n')
    outfile.write('\n')

  outfile.close()

  return toppatterns, patternnames

def showarticles(titles, toppatterns, patternnames, out='articles.txt'):
  outfile = file(out, 'w')

  # Loop over all the articles
  for j in range(len(titles)):
    outfile.write(titles[j].encode('utf8')+'\n') 

    # Get the top features for this article and 
		# reverse sort them
    toppatterns[j].sort()
    toppatterns[j].reverse()

    # Print the top three patterns
    for i in range(3):
      outfile.write(str(toppatterns[j][i][0]) + ' ' +
        str(patternnames[toppatterns[j][i][1]]) + '\n')
    outfile.write('\n')

  outfile.close()
      
			
