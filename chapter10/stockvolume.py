# -*- coding: utf-8 -*-

import nmf
import urllib2
from numpy import *

tickers = ['YHOO', 'AVP', 'BIIB', 'BP', 'CL', 'CVX',
            'EXPE', 'GOOG', 'PG', 'XOM', 'AMGN',
            'AMZN', 'AAPL']

shortest = 300
prices = {}
dates = None 

for t in tickers:
  # Open the URL
  print('%s ...' % t)
  rows = urllib2.urlopen('http://chart.finance.yahoo.com/table.csv?' + \
        's=%s&a=7&b=24&c=2006&d=7&e=24&f=2016&g=d&ignore=.csv' % t).readlines()
  # Extract the volume field from every line
  prices[t] = [float(r.split(',')[5]) for r in rows[1:] if r.strip() != '']
  if len(prices[t]) < shortest: shortest = len(prices[t])

  if not dates:
    dates = [r.split(',')[0] for r in rows[1:] if r.strip() != '']

l1 = [[prices[tickers[i]][j] for i in range(len(tickers))] 
        for j in range(shortest)]

w, h = nmf.factorize(matrix(l1), pc=5)
#print h
#print w

# Loop over all the features
for i in range(shape(h)[0]):
  print "Feature %d" % i

  # Get the top stocks for this feature
  ol = [(h[i,j], tickers[j]) for j in range(shape(h)[1])]
  ol.sort()
  ol.reverse()
  for j in range(len(tickers)):
    print ol[j]
  print

  # Show the top dates for this feature 
  porder = [(w[d,i], d) for d in range(shortest)]
  porder.sort()
  print [(p[0], dates[p[1]]) for p in porder[0:3]]
  print

