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
def getRecommendations(prefs, person, similarity=sim_pearson):
	totals = {} # (other 의 평점 x 나와의 유사도) 합계, 나와의 유사도 가중치
	simSums = {}

	for other in prefs:
		if other == person: continue
		sim = similarity(prefs, person, other)
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
	
		






