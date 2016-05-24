# -*- coding: utf-8 -*-

from math import sqrt
from PIL import Image, ImageDraw
import random

# 파일을 읽고 잘라서 반환한다. 
def readfile(filename):
  lines = [line for line in file(filename)]

  # 첫째줄은 단어 컬럼들이다. 
  colnames = lines[0].strip().split('\t')[1:]
  # 블로그 이름들 
  rownames = []
  data = []

  for line in lines[1:]:
    p = line.strip().split('\t')
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
    closest = distance(clust[0].vec, clust[1].vec)

    # 전체 벡터들에서 가장 가까운 두 개의 벡터 세트를 찾는다. 
    for i in range(len(clust)):
      for j in range(i+1, len(clust)):
        # 캐쉬된 결과가 없다면 계산해서 추가 
        if (clust[i].id, clust[j].id) not in distances:
          distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)
        d = distances[(clust[i].id, clust[j].id)]

        # 가장 가까운 결과를 갱신한다. 
        if d < closest:
          closest = d 
          lowestpair = (i, j)

    # 두 벡터의 각 요소의 가운데 값을 구함
    mergevec = [(clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i])/2.0
    for i in range(len(clust[0].vec))]

    # 가장 가까운 두 벡터를 사용해서 새로운 cluster 를 만든다. 
    newclust = biclust(mergevec, left=clust[lowestpair[0]], 
      right = clust[lowestpair[1]], distance = closest, id = currentclustid)

    currentclustid -= 1
    # 합쳐진 벡터들은 삭제한다. 
    del clust[lowestpair[1]]
    del clust[lowestpair[0]]
    clust.append(newclust)

  return clust[0]

# hclust 의 결과를 text 로 출력한다. 
def printclust(clust, labels=None, n=0):
  for i in range(n): print ' ',
  # 음수는, 두 개의 벡터가 합쳐진 브랜치를 뜻한다. 
  if clust.id < 0:
    print '-'
  else:
    if labels == None: print clust.id 
    else: print labels[clust.id]

  if clust.left != None: printclust(clust.left, labels = labels, n = n+1)
  if clust.right != None: printclust(clust.right, labels = labels, n = n+1)


################################################################################
# 여기서부터는 dendrogram 을 그리는 부분
################################################################################

# cluster 의 높이를 반환한다.
def getheight(clust):
  # leaf node 의 높이는 1
  if clust.left == None and clust.right == None: return 1

  # branch node 라면 left 와 right 의 합
  return getheight(clust.left) + getheight(clust.right)

def getdepth(clust):
  # leaf node 는 depth 가 0
  if clust.left == None and clust.right == None: return 0

  # bracnh node 라면 자신의 distance 와 하위 노드들의 depth 중 큰 것을 더한다. 
  return max(getdepth(clust.left), getdepth(clust.right)) + clust.distance

# 덴드로그램을 그린다. 
def drawdendrogram(clust, labels, jpeg = 'clusters.jpeg'):
  # 한 node 의 크기는 20pix 로 한다. 
  h = getheight(clust)*20
  w = 1200
  depth = getdepth(clust)

  scaling = float(w-150)/depth

  img = Image.new('RGB', (w, h), (255, 255, 255))
  draw = ImageDraw.Draw(img)
  # 시작 꼭지선
  draw.line((0, h/2, 10, h/2), fill = (255, 0, 0))

  drawnode(draw, clust, 10, (h/2), scaling, labels)
  img.save(jpeg, 'JPEG')

# node 를 그린다. 
def drawnode(draw, clust, x, y, scaling, labels):
  # branch node 라면 
  if clust.id < 0:
    h1 = getheight(clust.left) * 20
    h2 = getheight(clust.right) * 20
    top = y-(h1+h2)/2
    bottom = y+(h1+h2)/2


    # 수직선 
    draw.line((x, top+h1/2, x, bottom - h2/2), fill=(255, 0, 0))

    # 수평선 길이 즉, depth
    ll = clust.distance * scaling
    draw.line((x, top+h1/2, x+ll, top+h1/2), fill=(255, 0, 0))
    draw.line((x, bottom-h2/2, x+ll, bottom-h2/2), fill=(255,0,0))

    # 하위 노드들을 그린다. 
    drawnode(draw, clust.left, x+ll, top+h1/2, scaling, labels)
    drawnode(draw, clust.right, x+ll, bottom-h2/2, scaling, labels)

  # leaf node 라 blog name 을 출력한다. 
  else:
    draw.text((x+5, y-7), labels[clust.id], (0, 0, 0))


# 매트릭스를 회전시킨다. 
def rotatematrix(data):
  newdata = []
  for i in range(len(data[0])):
    newrow = [data[j][i] for j in range(len(data))]
    newdata.append(newrow)
  return newdata

################################################################################
# kmeans algorithm
################################################################################
def kcluster(rows, distance=pearson, k=4):
  # 개별 column vector 의 (min, max) 값을 구해서 전체 컬럼의 minmax 리스트를 만든다. 
  ranges = [(min(row[i] for row in rows), max(row[i] for row in rows)) 
  for i in range(len(rows[0]))]

  # k 개의 임의 벡터를 만든다. 
  clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]
  for i in range(len(rows[0]))] for j in range(k)]

  lastmatches = None 
  # 반복작업 횟수 설정
  for t in range(100):
    print 'Iteration %d' % t
    # 각 cluster 에 할당되는 vector 을 저장할 리스트 
    bestmatches = [[] for i in range(k)]

    # 각 row 를 k 개의 클러스터에 할당한다. 
    for j in range(len(rows)):
      row = rows[j]
      bestmatch = 0
      for i in range(k):
        d = distance(clusters[i], row)
        if d < distance(clusters[bestmatch], row): bestmatch = i
      bestmatches[bestmatch].append(j)

    # bestmatches 가 이전 loop 의 결과와 같다면 빠져나간다. 
    if bestmatches == lastmatches: break
    lastmatches = bestmatches

    # 각 클러스터의 중심을 구한다. 
    for i in range(k):
      avgs = [0.0] * len(rows[0])
      if len(bestmatches[i]) > 0:
        for rowid in bestmatches[i]:
          # 각 컬럼의 값을 누적한다. 
          for m in range(len(rows[rowid])):
            avgs[m] += rows[rowid][m]
          # 각 컬럼을 평균을 구한다.
        for j in range(len(avgs)):
          avgs[j] /= len(bestmatches[i])
        clusters[i] = avgs

  return bestmatches


# tanamoto 계수 
def tanamoto(v1, v2):
  c1, c2, shr = 0, 0, 0
  for i in range(len(v1)):
    if v1[i] != 0: c1 += 1
    if v2[i] != 0: c2 += 1
    if v1[i] != 0 and v2[i] != 0: shr += 1

  return 1.0 - (float(shr) / (c1 + c2 - shr))

################################################################################
# data 를 2차원 좌표로 나타낸 묶음을 반환한다. 
def scaledown(data, distance=pearson, rate=0.01):
  n = len(data)

  # 각 vector 의 실제거리를 구한다. 
  realdist = [[distance(data[i], data[j]) for j in range(n)] for i in range(0, n)]

  outersum = 0.0

  # 2차원 좌표 위의 임의의 n개 점을 설정한다. 
  loc = [[random.random(), random.random()] for i in range(n)]
  # 2차원 위 각 점 사이의 거리를 저장할 변수 
  dist2d = [[0.0 for j in range(n)] for i in range(n)]

  lasterror = None
  for m in range(0, 1000):
    # 각 점 사이의 거리를 구합시다. 
    for i in range(n):
      for j in range(n):
        # 동일한 점 사이의 거리는 구할 필요가 없다. 어차피 0
        if i == j: continue
        dist2d[i][j] = sqrt(sum([pow(loc[i][x] - loc[j][x], 2) for x in range(len(loc[i]))]))

    # 각 점의 위치를 보정할 값을 설정한다. 
    grad = [[0.0, 0.0] for i in range(n)]

    totalerror = 0
    for i in range(n):
      for j in range(n):
        if i == j: continue
        # 거리 매트릭스는 대각선을 기준으로 대칭이므로 (i, j) 나 (j, i)나 동일하다. 
        # 책에서는 굳이 왜 (j, i) 라고 썼을까?

        # 2차원거리와 실제거리의 차이를 비율을 구한다. 거리가 비슷하다면 0에 가까울 것이고 
        # 차이가 난다면 값이 커진다. 
        errorterm = (dist2d[j][i] - realdist[j][i])/realdist[j][i]

        # i점의 x, y 위치를 보정할 계수. j와의 차이 값들을 누적한다.  
        # dist2d 와 나누는 이유는? 내 생각으로는, 너무 휙휙 많이 움직이지 않기 위해서... 
        # dist2d 로 나누게 되면 현재의 i, j을 삼각형으로 한 cos, sin 값이 나오는데 
        # 이 값은 0과 1 사이이다. 
        grad[i][0] += ((loc[i][0] - loc[j][0])/dist2d[j][i]) * errorterm
        grad[i][1] += ((loc[i][1] - loc[j][1])/dist2d[j][i]) * errorterm

        # print "(%d, %d) = %f" % (i, j, errorterm)
        totalerror += abs(errorterm)
    print "%dth : %f" % (m, totalerror)

    if lasterror and lasterror < totalerror: break
    lasterror = totalerror

    # 점들의 위치를 이동한다. 
    for k in range(n):
      loc[k][0] -= rate * grad[k][0]
      loc[k][1] -= rate * grad[k][1]

  return loc

# 2D 로 표현된 데이터
def draw2d(data, labels, jpeg='mds2d.jpg'):
  img = Image.new('RGB', (2000, 2000), (255, 255, 255))
  draw = ImageDraw.Draw(img)

  for i in range(len(data)):
    x = (data[i][0] + 0.5) * 1000
    y = (data[i][1] + 0.5) * 1000
    draw.text((x, y), labels[i], (0, 0, 0))
  img.save(jpeg, 'JPEG')

























