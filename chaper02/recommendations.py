# -*- coding: utf-8 -*-

# A dictionary of movie critics and their ratings of a small
# set of movies
critics={
'Hojoon Ji': {'Superman Returns': 2.0, 'Snakes on a Plane': 3.0},
'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}


from math import sqrt

# tanimoto score 를 반환한다. 
# 0 ~ 1 사이의 값. 비슷할수록 1에 가깝다. 
def sim_tanimoto(prefs, p1, p2):
	l1 = prefs[p1].keys()
	print(l1)
	l2 = prefs[p2].keys()
	print(l2)
	c = [commonItem for commonItem in l1 if commonItem in l2]
	print(c)
	score = float(len(c)) / (len(l1) + len(l2) - len(c))
	return score


# euclidean dinstance 의 역을 반환 
def sim_distance(prefs, person1, person2):
	# 두 사람 모두에게 포함된 영화들이 있나 살펴본다.
	si = {}
	for item in prefs[person1]:
		if item in prefs[person2]:
			si[item] = 1

	# 공통된 영화가 없다면 두 사람의 상관관계는 0이다. 
	if len(si) == 0: return 0

	# euclidean distance 를 구한다. 
	sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
		for item in prefs[person1] if item in prefs[person2]])
	# 자신과의 상관관계는 1이고 상관관계가 클수록 큰 숫자가 나오기 위해 역함수를 취한다. 
	return 1/(1+sqrt(sum_of_squares))

# pearson correlation coefficient 를 반환
def sim_pearson(prefs, p1, p2):
		# 두 사람 모두에게 포함된 영화들이 있나 살펴본다.
	si = {}
	for item in prefs[p1]:
		if item in prefs[p2]:
			si[item] = 1

	# 공통된 영화가 없다면 두 사람의 상관관계는 0이다. 
	n = len(si)
	if n == 0: return 0

	# 선호도 합
	sum1 = sum([prefs[p1][movie] for movie in si])
	sum2 = sum([prefs[p2][movie] for movie in si])

	# 제곱의 합
	sum1sq = sum([pow(prefs[p1][movie], 2) for movie in si])
	sum2sq = sum([pow(prefs[p2][movie], 2) for movie in si])

	# p1 과 p2 의 곱의 합
	pSum = sum([prefs[p1][movie]*prefs[p2][movie] for movie in si])

	# person 공식
	num = pSum - (sum1*sum2/n)
	den = sqrt((sum1sq-pow(sum1, 2)/n)*(sum2sq-pow(sum2, 2)/n))
	if den == 0: return 0
	r = num/den
	return r

# person 과 유사항 성향을 갖는 사람들을 찾는다. 
def topMatches(prefs, person, n = 5, similarity = sim_pearson):
	scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]

	scores.sort()
	scores.reverse()
	return scores[0:n]

# 모든 리뷰어 데이터를 사용해서 추천 데이터를 가져온다. 
# 내가 평가하지 않은 데이터에 한해서 추천을 받는다. 
# [수정사항]
# 2016.04.29 모든 사람과 비교하지 않고 '사용자 유사도 풀' 에서만 비교한다.
def getRecommendations(prefs, usersim, person):
	totals = {} # (other 의 평점 x 나와의 유사도) 합계, 나와의 유사도 가중치
	simSums = {}

	for (sim, other) in usersim[person]:
		if sim <= 0: continue

		for item in prefs[other]:
			# 내 평가에 없었던 항목들만 대상으로 삼는다. 
			if item not in prefs[person] or prefs[person][item] == 0:
				totals.setdefault(item, 0)
				totals[item] += prefs[other][item] * sim
				simSums.setdefault(item, 0)
				simSums[item] += sim

	# 가중평가된 합을 유사도 합으로 나눈다. 
	# 더 객관적인 자료라고 할 수 있다.
	rankings = [(total/simSums[item], item) for item, total in totals.items()]	
	rankings.sort()
	rankings.reverse()
	return rankings

# dictionary 의 안과 밖을 바꾼다.	
def transformPrefs(prefs):
	result = {}
	
	for person in prefs:
		for item in prefs[person]:
			result.setdefault(item,{})
			result[item][person] = prefs[person][item]
	return result

# 항목 간 유사한 항목들의 유사도 점수를 계산한다. 
def calculateSimilarItems(prefs, n=10):
	result = {}

	# 항목 기반으로 변경한다. 
	itemPrefs = transformPrefs(prefs)
	c = 0
	for item in itemPrefs:
		c += 1
		if c % 100 == 0: print "%d / %d" % (c, len(itemPrefs))
		scores = topMatches(itemPrefs, item, n = n, similarity = sim_distance)
		result[item] = scores

	return result

# 사용자간 유사도를 구한다. 
def calculateSimilarUsers(prefs, n=10):
	result = {}

	c = 0	
	for user in prefs:
		c += 1
		if c % 100 == 0: print "%d / %d" % (c, len(prefs))
		scores = topMatches(prefs, user, n = n, similarity = sim_distance)
		result[user] = scores 
		
	return result
		

# prefs => 사용자, 항목의 점수 matrix
# itemMatch => 항목간의 유사도
# user
# 미리 생성된 항목유사도를 기준으로 user 에게 항목을 추천한다. 
def getRecommendedItems(prefs, itemMatch, user):
	userRatings = prefs[user]
	scores = {}
	totalSim = {}

	for (item, rating) in userRatings.items():
		# 미리 생성된 유사도 묶음에서 item 에 해당하는 리스트를 가져온다. 
		for (similarity, item2) in itemMatch[item]:
			# 유저가 평가한 아이템이라면 다음 아이템으로 넘어간다. 
			if item2 in userRatings: continue

			scores.setdefault(item2, 0)
			# 유사도 * item 평가점수 => 가중치를 부여한다. 
			scores[item2] += similarity * rating

			totalSim.setdefault(item2, 0)
			totalSim[item2] += similarity

	rankings = [(score/totalSim[item], item) for item, score in scores.items()]
	rankings.sort()
	rankings.reverse()
	return rankings


# MovieLens 데이터를 로딩한다. 
def loadMovieLens(path='./ml-100k'):
	# 영화제목
	movies = {}
	for line in open(path + '/u.item'):
		(id, title) = line.split('|')[0:2]
		movies[id] = title

	# 유저별 영화점수 데이터를 생성한다. 
	prefs = {}
	for line in open(path + '/u.data'):
		(user, movieID, rating, ts) = line.split('\t')
		prefs.setdefault(user, {})
		prefs[user][movies[movieID]] = float(rating)

	return prefs




		
	
	
	
		






