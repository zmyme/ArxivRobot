from lib.parser import dom_node
from lib import utils


class feed_manager():
	def __init__(self, submgr, arxivbot, style='./config/style.css'):
		self.style_path = style
		self.style = ''
		self.bot = arxivbot
		self.submgr = submgr
		self.update_style()

	def update_style(self, path = None):
		if path is None:
			path = self.style_path
		print('loading style from:', path)
		with open(path, 'r') as f:
			self.style = f.read()
			self.style += '\n'

	def fetch_today_feed(self):
		self.today_feed = self.bot.get_today_feed()

	def filter_papers_for_user(self, subscriber):
		strong_papers = []
		weak_papers = []
		keywords = subscriber['keywords']
		papers = []
		for topic in subscriber['topics']:
			if topic in self.today_feed:
				papers += self.today_feed[topic]
			else:
				print('Warning: topic {0} is subscribed but not downloaded!'.format(topic))
		known_ids = []
		unique_papers = []
		for paper in papers:
			paper_id = paper.arxiv_id
			if paper_id not in known_ids:
				unique_papers.append(paper)
				known_ids.append(paper_id)
		print('removing {0} repeated papers.'.format(len(papers) - len(unique_papers)))
		papers = unique_papers
		for paper in papers:
			strong = False
			weak = False
			for keyword in keywords:
				if paper.info['title'].lower().find(keyword) != -1:
					strong = True
					break;
				elif paper.info['abstract'].lower().find(keyword) != -1:
					weak = True
			if strong:
				strong_papers.append(paper)
			elif weak:
				weak_papers.append(paper)
		return strong_papers, weak_papers

	def generate_group_feed(self, paper_groups):
	    group_html = ''
	    for key in paper_groups:
	        header = dom_node('paper-group')
	        header.data = key
	        group_html += header.to_string() + '\n'
	        for paper in paper_groups[key]:
	            group_html += paper.to_html() + '\n'
	    return group_html

	def generate_daily_feed_by_matched_paper(self, strong_interested, weak_interested):
		feeds = {}
		if len(strong_interested) > 0:
			feeds['Strong Interested Paper'] = strong_interested
		if len(weak_interested) > 0:
			feeds['Weak Interested Paper'] = weak_interested
		xml_feed = self.generate_group_feed(feeds)
		return xml_feed

	def generate_daily_email_by_matched_paper(self, strong_interested, weak_interested):
		xml_feed = self.generate_daily_feed_by_matched_paper(strong_interested, weak_interested)
		email_content = ''
		if xml_feed != '':
			email_content = self.style + xml_feed
		return email_content

	def generate_daily_emails(self):
		self.fetch_today_feed()
		emails = {}
		# email is a dict, containing title, reciver and content.
		today = utils.str_day()
		for name in self.submgr.subscribers:
			subscriber = self.submgr.subscribers[name]
			strong, weak = self.filter_papers_for_user(subscriber)
			content = self.generate_daily_email_by_matched_paper(strong, weak)
			reciver = subscriber['email']
			if content == '':
				print('Skipping user {0} [{1}] since no paper matched.'.format(name, reciver))
				continue;
			title = "Your Interested Paper On Arxiv Today ({0})".format(today)
			email = {}
			email['reciver'] = reciver
			email['title'] = title
			email['content'] = content
			emails[name] = email
		return emails
