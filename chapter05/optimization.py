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

# 시간을 분단위로 변환한다. 
def getMinutes(t):
  x = time.strptime(t, "%H:%M")
  return x[3]*60 + x[4]

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

  # 도착시, 출발시 기다리는 시간을 설정한다. 
  totalWait = 0
  for d in range(len(sol)/2):
    origin = people[d][1]
    outbound = flights[(origin, destination)][int(sol[2*d])]
    returnf = flights[(destination, origin)][int(sol[2*d+1])]

    totalWait += latestArrival - getMinutes(outbound[1])
    totalWait += getMinutes(returnf[0]) - earliestDep

  # 자동차 렌탈 고려
  if latestArrival > earliestDep: totalPrice += 50  
  return totalPrice + totalWait

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
  return r

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
    if newVec[sel] < domain[sel][0]: newVec[sel] = domain[sel][0]
    if newVec[sel] > domain[sel][1]: newVec[sel] = domain[sel][1]

    # 비용을 계산한다.
    cost = costf(vec)
    newCost = costf(newVec)

    # 초기에는 T 가 크기 때문에 높은 확률이 나온다. 
    p = pow(math.e, -(newCost - cost)/T)

    # 특정상황에서 솔류션을 교체한다. 
    if (newCost < cost or random.random() < p): vec = newVec

    T = T * cool

  return vec

    







