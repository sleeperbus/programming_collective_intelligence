# -*- coding: utf-8 -*-

# 파일을 읽고 잘라서 반환한다. 
def readfilie(filename):
  lines = [line for line in file(filename)]

  # 첫째줄은 단어 컬럼들이다. 
  colnames = lines[0].strip().split('\t')[1:]
  # 블로그 이름들 
  rownames = []
  data = []

  for line in lines[1:]:
    p = line.strip.split('\t')
    rownames.append(p[0])
    data.append([float(x) for x in p[1:]])
  return rownames, colnames, data

# pearson 계수를 구한다. 
def pearson(v1,v2):
  # Simple sums
  sum1=sum(v1)
  sum2=sum(v2)
  
  # Sums of the squares
  sum1Sq=sum([pow(v,2) for v in v1])
  sum2Sq=sum([pow(v,2) for v in v2])  
  
  # Sum of the products
  pSum=sum([v1[i]*v2[i] for i in range(len(v1))])
  
  # Calculate r (Pearson score)
  num=pSum-(sum1*sum2/len(v1))
  den=sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
  if den==0: return 0

  # 상관관계가 클수록 작은 수를 반환하기 위해서 1의 보수를 취함
  return 1.0-num/den

# 두 벡터가 합쳐진 결과벡터이다. 
class biclust:
  def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
    self.left = left
    self.right = right
    self.vec = vec 
    self.id = id 
    self.distance = distance

# 계층적 구조를 만든다. 
def hclust(rows, distance=pearson):
  # 각 vector 들의 거리값을 캐쉬한다. 
  distances = {}
  # 합쳐진 vector 들은 음수값을 갖는다. 
  currentclustid = -1

  # 단어벡터로 킄래스를 만든다. 
  clust = [biclust(rows[i], id=i) for i in range(len(rows))]

  while len(clust) > 1:
    lowestpair = (0, 1)
    closest = distance(clust[0].vec, clust[i].vec)

    # 전체 벡터들에서 가장 가까운 두 개의 벡터 세트를 찾는다. 
    for i in range(len(clust)):
      for j in range(i+1, len(clust)):
        # 캐쉬된 결과가 없다면 계산해서 추가 
        if (clust[i].id, clust[j].id) not in distances:
          distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)
        d = distances(clust[i].id, clust[j].id)

        # 가장 가까운 결과를 갱신한다. 
        if d < closest:
          closest = d 
          lowestpair = (i, j)















