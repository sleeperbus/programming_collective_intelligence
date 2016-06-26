# -*- coding: utf-8 -*-
import re 
import math 

def getwords(doc):
  splitter = re.compile('\\W*')
  words = [s.lower() for s in splitter.split(doc) if len(s) > 2 and len(s) < 20]
  return dict([(w, 1) for w in words])
  
def sampletrain(cl):
  cl.train('Nobody owns the water.', 'good')
  cl.train('the quick rabbit jumps fences', 'good')
  cl.train('buy pharmceuticals now', 'bad')
  cl.train('make quick money at the online casino', 'bad')
  cl.train('the quick brown fox jumps', 'good')
  
class classifier:
  def __init__(self, getFeatures, filename=None):
    self.fc = {}
    self.cc = {}
    self.getFeatures = getFeatures
  
  # feature 에 대한 결과분류값을 증가시킨다.
  # 예를 들어 'spam' 에 'bad' 라는 분류값을 증가시킨다.
  def incf(self, f, cat):
    self.fc.setdefault(f, {})
    self.fc[f].setdefault(cat, 0)
    self.fc[f][cat] += 1
  
  # 결과분류값을 증가시킨다.  
  # 예를 들어 'good' 이라는 분류값을 증가시킨다.
  def incc(self, cat):
    self.cc.setdefault(cat, 0)
    self.cc[cat] += 1
   
  # 특정 feature 의 category 개수를 반환한다. 
  # 예를 들어 'spam' 이라는 feature 에서 'good' 이라고 분류된 개수
  def fcount(self, f, cat):
    if f in self.fc and cat in self.fc[f]:
      return float(self.fc[f][cat])
    return 0.0
  
  # 특정 category 에 속한 개수를 반환한다.  
  # 예를 들어 'good' 이라고 결정된 문서수
  def catcount(self, cat):
    if cat in self.cc:
      return self.cc[cat]
    return 0
  
  # 전체 분류개수를 반환한다. 예를 들어 전체 문서수 
  def totalcount(self):
    return sum(self.cc.values())
    
  def train(self, item, cat):
    features = self.getFeatures(item)
    for f in features: self.incf(f, cat)
    self.incc(cat)
    

    
  
  