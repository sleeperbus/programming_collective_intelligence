# -*- coding: utf-8 -*-
import feedparser 
import re 

# 피드에서 추출한 엔트리들의 제목과 단어 출현 횟수를 딕셔너리로 반환한다. 
def getwordcounts(url):
	print('%s progressing' % url)	
	d = feedparser.parse(url)
	wc = {}

	for e in d.entries:
		if 'summary' in e: summary = e.summary 
		else: summary = e.description

		# 단어 목록 추출 
		words = getwords(e.title + ' ' + summary)
		for word in words:
			wc.setdefault(word, 0)
			wc[word] += 1

	try:
		title = d.feed.title 
	except Exception, e:
		title = "no title"
	return title, wc

# 단어 몪음을 반환한다. 
def getwords(html):
	# HTML 태그 제거
	txt = re.compile(r'<[^>]+>').sub('', html)
	# 알파벳 문자들만 취급
	words = re.compile(r'[^A-Z^a-z]+').split(txt)
	# 소문자로 변환
	return [word.lower() for word in words if word != '']



apcount = {}
wordcounts = {}
feedlist = []
for feedurl in file('feedlist.txt'):
	feedlist.append(feedurl)
	title, wc = getwordcounts(feedurl)
	wordcounts[title] = wc 
	for word, count in wc.items():
		apcount.setdefault(word, 0)
		# 해당 블로그에 특정 단어가 한 번 이상 등장해야 apcount 를 증가시킨다. 
		if count > 1:
			apcount[word] += 1

wordlist = []
# 단어 묶음을 만든다. 적게 등장하거나 많이 등장한 단어는 뺀다. the 같은 정관사 종류는 엄청 많이 
# 등장할 것이니 빼야한다. 아래의 비율은 조절될 수 있다. 
for w, bc in apcount.items():
	frac = float(bc)/len(feedlist)
	if frac > 0.1 and frac < 0.5: wordlist.append(w)

out = file('blogdata.txt', 'w')
out.write('Blog')
for word in wordlist: out.write('\t%s' % word)
out.write('\n')
for blogTitle, wc in wordcounts.items():
	try:
		out.write(blogTitle)
	except Exception, e:
		out.write("Just Blog")
	for word in wordlist:
		if word in wc: out.write('\t%d' % wc[word])
		else: out.write('\t0')
	out.write('\n')

