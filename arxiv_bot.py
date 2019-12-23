import arxiv_spider
import os
import time
from lib import utils

# cache tree:
# cache_root
# 	- topic-caches
# 	  	- feed_$(time).arxiv_feed
# 		- feed_year_$(year).arxiv_feed

class arxiv_bot():
	def __init__(self, topics, cache_dir='./cache', arxiv_site='https://arxiv.org', log=False):
		self.log = log
		self.site = arxiv_site
		self.topics = []
		self.spiders = {}
		self.cache_dir = cache_dir
		self.topic_caches = {}
		if not os.path.isdir(self.cache_dir):
			os.makedirs(self.cache_dir)
		self.update_topics(topics)

	def update_topics(self, topics):
		for topic in topics:
			if topic not in self.topics:
				self.topics.append(topic)
				if self.log:
					print('Adding topic {0}.'.format(topic))
				topic_cache = os.path.join(self.cache_dir, topic)
				self.topic_caches[topic] = topic_cache
				if not os.path.isdir(topic_cache):
					if self.log:
						print('creating topic dir:', topic_cache)
					os.makedirs(topic_cache)
				self.spiders[topic] = arxiv_spider.arxiv_spider(topic, self.site)

	# load feed if it is already downloaded. If not, use spiders to get today's feed.
	def get_today_feed(self):
		today_feed = {}
		today = utils.str_day()
		for topic in self.topics:
			today_feed_name = 'feed_' + today + '.arxiv_daily_feed'
			today_feed_path = os.path.join(self.cache_dir, topic, today_feed_name)
			cache_dir = self.topic_caches[topic]
			topic_feed = None
			if os.path.exists(today_feed_path):
				topic_feed = utils.load_python_object(today_feed_path)
			else:
				topic_feed = self.spiders[topic].get_today_paper()
				print('Fetching topic {0} papers...'.format(topic))
				for paper in topic_feed:
					if self.log:
						print('download abstract for paper', paper.info['title'])
					paper.download_abstract()
				utils.save_python_object(topic_feed, today_feed_path)
			today_feed[topic] = topic_feed
		return today_feed

	def get_interested_paper(self, topic, keywords):
		if self.today_feed is None or utils.str_day() is not self.today:
			self.today_feed = self.get_today_feed()
			self.today = utils.str_day()
			print('Updating daily feed.')

		topic_feed = self.today_feed[topic]
		topic_papers = []
		for day in topic_feed:
			topic_papers += topic_feed[day]
		strong = []
		weak = []
		for paper in topic_papers:
			strong_match = False
			weak_match = False
			for keyword in keywords:
				if paper.info['title'].lower().find(keyword) != -1:
					strong_match = True
					break
				elif paper.info['abstract'].lower().find(keyword) != -1:
					weak_match = True
			if strong_match:
				strong.append(paper)
			elif weak_match:
				weak.append(paper)
		return strong, weak
