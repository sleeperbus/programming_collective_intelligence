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
      return float(self.cc[cat])
    return 0.0
  
  # 전체 분류개수를 반환한다. 예를 들어 전체 문서수 
  def totalcount(self):
    return sum(self.cc.values())
   
  # 분류를 반환한다. 
  def categories(self):
    return self.cc.keys()
    
  def train(self, item, cat):
    features = self.getFeatures(item)
    for f in features: self.incf(f, cat)
    self.incc(cat)
  
  # 특정 feature 가 어떤 분류에 있을 확률  
  def fprob(self, f, cat):
    if self.catcount(cat) == 0: return 0
    return self.fcount(f, cat) / self.catcount(cat)
    
  # 가중확률 
  # 출현빈도가 낮은 단어에 대해 적절한 보정처리를 한다.
  def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
    basicprob = prf(f, cat)
    totals = sum([self.fcount(f, c) for c in self.categories()])
    bp = ((weight*ap)+(totals*basicprob))/(weight+totals)
    return bp
    
 
class naivebayes(classifier):
  def __init__(self, getFeatures):
    classifier.__init__(self, getFeatures)
    self.thresholds= {}
  
  def docprob(self, item, cat):
    features = self.getFeatures(item)
    
    p = 1
    for f in features: p *= self.weightedprob(f, cat, self.fprob)
    return p
  
  # bayes's theorm
  # P(Cat|Doc) = P(Doc|Cat) * (P(Cat)/P(Doc))  
  # 여기서 P(Doc) 은 1로 생각한다.
  def prob(self, item, cat):
    catprob = self.catcount(cat)/self.totalcount()
    docprob = self.docprob(item, cat)
    return docprob * catprob
  
  # 분류에 대한 임계치 설정  
  def setthreshold(self, cat, t):
    self.thresholds[cat] = t
  
  # 분류에 대한 임계치 반환  
  def getthreshold(self, cat):
    if cat not in self.thresholds: return 1.0
    return self.thresholds[cat]
  
  # item 의 분류를 정한다.
  # 가중치가 설정된 분류의 경우, 가중치를 설정해서 선택된 분류를 사용할 
  # 것인지 결정한다.
  def classify(self, item, default=None):
    probs = {}
    max = 0.0
    # 가장 높은 확률의 분류를 찾는다.
    for cat in self.categories():
      probs[cat] = self.prob(item, cat)
      if probs[cat] > max:
        max = probs[cat]
        best = cat
        
    for cat in probs:
      if cat == best: continue
      # 타분류 * 가중치 > 가장높은확률 을 넘지 못하면, 기본값을 반환한다.
      if probs[cat] * self.getthreshold(best) > probs[best]: return default
    return best
    

class fisherclassifier(classifier):
  # P(F|CAT)
  # feature 가 특정 cat 에 속할 확률, 즉 전체 cat 중에서 특정 cat 에 
  # 속할 확률을 구한다.
  def cprob(self, f, cat):
    clf = self.fprob(f, cat)
    if clf == 0: return 0 
    
    freqsum = sum([self.fprob(f, c) for c in self.categories()])
    p = clf / (freqsum)
  