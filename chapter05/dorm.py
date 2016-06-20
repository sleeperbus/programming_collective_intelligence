# -*- coding: utf-8 -*-
import random 
import math 

dorms = ["Zeus", "Athena", "Hercules", "Bacchus", "Pluto"]
prefs = [
    ("Toby", ("Bacchus", "Hercules"))
    , ("Steve", ("Zeus", "Pluto"))
    , ("Andrea", ("Athena", "Zeus"))
    , ("Sarah", ("Zeus", "Pluto"))
    , ("Dave", ("Athena", "Bacchus"))
    , ("Jeff", ("Hercules", "Pluto"))
    , ("Fred", ("Pluto", "Athena"))
    , ("Suzie", ("Bacchus", "Hercules"))
    , ("Laura", ("Bacchus", "Hercules"))
    , ("Neil", ("Hercules", "Athena"))
    ]

# 1번 학생의 선택 범위는 0~9번 방
# 2번 학생의 선택 범위는 0~8번 방
domain = [(0, (len(dorms)*2)-i-1) for i in range(0, len(dorms)*2)]

# solution 을 출력한다.
def printSolution(sol):
  slots = []
  
  # dorm 마다 방이 2개씩 있다. 방을 10개로 가정한다.
  for i in range(len(dorms)): slots += [i, i]
  
  for i in range(len(sol)):
    # i번째 학생이 원하는 방 
    x = int(sol[i])
    dorm = dorms[slots[x]]
    print prefs[i][0], dorm 
    del slots[x]

# 비용을 계산한다. 
# 1순위는 0, 2순위는 1, 순위 밖이면 3을 받는다.
def dormCost(sol):
  cost = 0
  slots = []
  for i in range(len(dorms)): slots += [i, i]
  
  for i in range(len(sol)):
    x = int(sol[i])
    assigned = dorms[slots[x]]
    pref = prefs[i][1]
    if pref[0] == assigned: cost += 0
    elif pref[1] == assigned: cost += 1 
    else: cost += 3
    
    del slots[x]
  
  return cost
    
    
    
    
  
    

    