from arxiv_spider import arxiv_paper
import utils
import numpy as np

authors = {}

years = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']

for year in years:
	print('Analysising year:', year)
	papers = utils.load_python_object('./feeds/' + year)
	for paper in papers:
		author_this_paper = paper.info['authors']
		for author in author_this_paper:
			author = utils.delete_n(author)
			if author in authors:
				authors[author] += 1
			else:
				authors[author] = 1

freq = []
names = []
for author in authors:
	freq.append(authors[author])
	names.append(author)

freq = np.asarray(freq, dtype=np.int32)

freq_sort = np.argsort(freq)

num_authors = len(names)

for i in range(num_authors):
	aid = freq_sort[num_authors - i - 1]
	print('Name: {0} | papers: {1}'.format(names[aid], freq[aid]).encode('utf-8'))


# keywords = {}

# years = ['2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']

# for year in years:
# 	print('Analysising year:', year)
# 	papers = utils.load_python_object('./feeds/' + year)
# 	for paper in papers:
# 		keyword_this_paper = paper.info['title'].split(' ')
# 		for keyword in keyword_this_paper:
# 			keyword = utils.delete_n(keyword).lower()
# 			if keyword in keywords:
# 				keywords[keyword] += 1
# 			else:
# 				keywords[keyword] = 1

# freq = []
# names = []
# for keyword in keywords:
# 	freq.append(keywords[keyword])
# 	names.append(keyword)
# freq = np.asarray(freq, dtype=np.int32)
# freq_sort = np.argsort(freq)
# num_keywords = len(names)

# for i in range(num_keywords):
# 	aid = freq_sort[num_keywords - i - 1]
# 	print('Keyword: {0} | papers: {1}'.format(names[aid], freq[aid]).encode('utf-8'))