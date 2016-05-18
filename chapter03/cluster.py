# -*- coding: utf-8 -*-

from math import sqrt
from PIL import Image, ImageDraw

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













