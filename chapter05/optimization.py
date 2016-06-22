# -*- coding: utf-8 -*-
import time
import random
import math 

people = [
  ("Syemour", "BOS")
  , ("Franny", "DAL")
  , ("Zooey", "CAK")
  , ("Walt", "MIA")
  , ("Buddy", "ORD")
  , ("Les", "OMA")
]

destination = "LGA"
flights = {}

# 비행 스케줄표를 만든다. 
for line in file("schedule.txt"):
  origin, dest, depart, arrive, price = line.strip().split(",")
  flights.setdefault((origin, dest), [])
  flights[(origin, dest)].append((depart, arrive, int(price)))

domain = [(0, 9)] * len(people) * 2

# 시간을 분단위로 변환한다. 
def getMinutes(t):
  x = time.strptime(t, "%H:%M")
  return x[3]*60 + x[4]

# 시간에서 시만 가져온다. 
def getHour(t):
  x = time.strptime(t, "%H:%M")
  return x[3]


# 리스트를 사람들이 알아볼 수 있는 형식으로 출력한다. 
def printSchedule(r):
  for d in range(len(r)/2):
    name = people[d][0]
    origin = people[d][1]
    out = flights[(origin, destination)][r[d*2]]
    ret = flights[(destination, origin)][r[d*2+1]]
    print "%10s%10s %5s-%5s $%3s %5s-%5s $%3s" % (name, origin, out[0], out[1], out[2],
      ret[0], ret[1], ret[2])

# 비용함수
def scheduleCost(sol):
  totalPrice = 0
  latestArrival = 0
  earliestDep = 24 * 60

  # 비행가격을 산출한다. 
  for d in range(len(sol)/2):
    origin = people[d][1]
    outbound = flights[(origin, destination)][int(sol[2*d])]
    returnf = flights[(destination, origin)][int(sol[2*d+1])]

    totalPrice += outbound[2]
    totalPrice += returnf[2]

    # 가장 늦은 도착시간, 가장 빠른 출발시간을 설정한다. 
    if latestArrival < getMinutes(outbound[1]): latestArrival = getMinutes(outbound[1])
    if earliestDep > getMinutes(returnf[0]): earliestDep = getMinutes(returnf[0])

  # 도착시, 출발시 기다리는 시간을 기준으로 페널티를 준다. 
  totalWait = 0
  for d in range(len(sol)/2):
    origin = people[d][1]
    outbound = flights[(origin, destination)][int(sol[2*d])]
    returnf = flights[(destination, origin)][int(sol[2*d+1])]

    totalWait += latestArrival - getMinutes(outbound[1])
    totalWait += getMinutes(returnf[0]) - earliestDep

  # 전체비행시간으로 비용을 산출한다. 
  totalTime = 0
  for d in range(len(sol)/2):
    origin = people[d][1]
    outbound = flights[(origin, destination)][int(sol[2*d])]
    returnf = flights[(destination, origin)][int(sol[2*d+1])]
    totalTime += getMinutes(outbound[1]) - getMinutes(outbound[0])
    totalTime += getMinutes(returnf[1]) - getMinutes(returnf[0])

  # 8시 이전에 출발하는 비행기에는 20달러 페널티
  toolEarly = 0
  for d in range(len(sol)/2):
    origin = people[d][1]
    outbound = flights[(origin, destination)][int(sol[2*d])]
    returnf = flights[(destination, origin)][int(sol[2*d+1])]

    if getHour(outbound[0]) <  8: toolEarly += 1
    if getHour(returnf[0]) <  8: toolEarly += 1

  # 자동차 렌탈 고려
  if latestArrival > earliestDep: totalPrice += 50  
  return totalPrice + totalWait + totalTime * 0.5 + toolEarly * 20

# 무작위 솔루션   
def randomOptimize(domain, costf):
  best = 999999999
  bestr = None 
  for i in range(10000):
    # create random solution 
    r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
    cost = costf(r)
    
    if cost < best:
      best = cost 
      bestr = r
  return bestr

# hill climb, 임의 솔루션을 선택한 뒤, 각 비행편의 앞뒤 비행편으로 바꾸었을 때의 비용을 구해본다.
def hillClimb(domain, costf):
  sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

  while 1:
    neighbors = []
    for j in range(len(domain)):
      # 현재 비행편의 앞뒤 비행편을 하나씩 선택한다. 
      if sol[j] > domain[j][0]:
        neighbors.append(sol[0:j] + [sol[j]+1] + sol[j+1:])
      if sol[j] < domain[j][1]:
        neighbors.append(sol[0:j] + [sol[j]-1] + sol[j+1:])

    current = costf(sol)
    best = current
    for j in (range(len(neighbors))):
      cost = costf(neighbors[j])
      if cost < best: 
        best = cost 
        sol = neighbors[j]
    # 비용이 기존과 같다면 break        
    if best == current: break

  return sol

# simulated annealing 
# 특정확률로 나쁜 답을 선택해서 local minimum 을 회피하려고 한다.
def annealingOptimize(domain, costf, T=10000.0, cool=0.95, step=1):
  # random initialize 
  vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

  # 온도는 cool 을 사용해서 감소시킨다. 
  while T > 0.1:
    # solution 중 임의의 비행편을 선택한다.
    sel = random.randint(0, len(domain)-1)

    # 변경할 방향을 선택한다. 
    dir = random.randint(-step, step)

    newVec = vec[:]
    newVec[sel] += dir 
    # 범위보정
    if newVec[sel] < domain[sel][0]: newVec[sel] = domain[sel][0]
    if newVec[sel] > domain[sel][1]: newVec[sel] = domain[sel][1]

    # 비용을 계산한다.
    cost = costf(vec)
    newCost = costf(newVec)
    print "cost: %f, newCost: %f" % (cost, newCost)

    # 초기에는 T 가 크기 때문에 높은 확률이 나온다. 
    p = pow(math.e, (-newCost - cost)/T)

    # 특정상황에서 솔류션을 교체한다. 
    if (newCost < cost or random.random() < p): vec = newVec

    T = T * cool

  return vec

# 유전자 알고리즘
# 한 세대마다 mutation crossover 를 거친다.
def geneticOptimize(domain, costf, popsize=50, step=1, mutprob=0.2, elite=0.2, maxiter=100):
  # mutation operation - 임의 항공편을 변경한다.
  def mutate(vec):
    sel = random.randint(0, len(domain)-1)
    if random.random() < 0.5 and vec[sel] > domain[sel][0]:
      return vec[0:sel] + [vec[sel]-step] + vec[sel+1:]
    elif vec[sel] < domain[sel][1]:
      return vec[0:sel] + [vec[sel]+step] + vec[sel+1:] 
    else: return vec
    
  # crossover operation - 두 개의 벡터를 교배한다.
  def crossover(r1, r2):
    sel = random.randint(0, len(domain)-2)
    return r1[0:sel] + r2[sel:]
    
  # build population 
  pop = []
  for i in range(popsize):
    vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
    pop.append(vec)
  
  # 매 세대마다 살아남을 vectors  
  topElite = int(elite*popsize)
  
  for i in range(maxiter):
    scores = [(costf(v), v) for v in pop]
    scores.sort() 
    ranked = [v for (s, v) in scores]
    
    # 다음 세대로 넘어갈 벡터들
    pop = ranked[0:topElite]
   
    # 모자란 세대를 보충한다.  
    while len(pop) < popsize:
      # mutation
      if random.random() < mutprob:
        # choose random vector from pop
        sel = random.randint(0, topElite)
        pop.append(mutate(ranked[sel]))
      else:
        # crossover 
        r1 = random.randint(0, topElite)
        r2 = random.randint(0, topElite)
        pop.append(crossover(ranked[r1], ranked[r2]))
    
    print scores[0][0]
    
  return scores[0][1]

# annealing 방식에 랜덤입력을 넣는다. 
def randomAnnealingOptimize(domain, costf):
  best = 999999999
  bestResult = None 

  for i in range(100):
    sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
    newCost = annealingOptimize(domain, costf)
    if newCost < best:
      print 'newCost: %f' % newCost
      best = newCost
      bestResult = sol
  return bestResult


      
    
  
    







