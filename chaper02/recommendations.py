# -*- coding: utf-8 -*-

# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
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


