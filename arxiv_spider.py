import requests
import pickle
import time
from lib import utils
from lib.parser import dom_node, simple_parser

import socket
import socks

use_proxy = False
if use_proxy:
    SOCKS5_PROXY_HOST = '127.0.0.1'
    SOCKS5_PROXY_PORT = 1080
    default_socket = socket.socket
    socks.set_default_proxy(socks.SOCKS5, SOCKS5_PROXY_HOST, SOCKS5_PROXY_PORT)
    socket.socket = socks.socksocket

class arxiv_paper():
    def __init__(self, arxiv_id = None, paper_info = None):
        self.arxiv_id = arxiv_id
        self.info = paper_info

    def add_author(self, author):
        self.info['authors'].append(authors)

    def title(self):
        return self.info['title']


    def describe(self):
        information = ''
        information += 'ID: {0} (https://arxiv.org/abs/{0})\n'.format(self.arxiv_id)
        for key in self.info:
            if self.info[key] is not None:
                info = utils.formal_text(self.info[key])
                information += ('\t' + key + ':' + str(info) + '\n')
        return information

    def show(self):
        print(self.describe())

    def to_html(self):
        dom_tree = dom_node(name = 'paper-section')
        paper_title = None
        paper_link = None
        paper_authors = None
        paper_comments = None
        paper_subjects = None
        paper_abstract = None
        for key in self.info:
            if self.info[key] is not None:
                if key == 'title':
                    paper_title = dom_node('paper-title')
                    link_attr = {'href':'https://arxiv.org/abs/{0}'.format(self.arxiv_id)}
                    link_node = dom_node('a', link_attr)
                    link_node.data = self.info[key]
                    paper_title.add_child(link_node)
                    paper_link = dom_node('paper-pdf-link')
                    pdf_link_attr = {'href':'https://arxiv.org/pdf/{0}'.format(self.arxiv_id)}
                    pdf_link = dom_node('a', pdf_link_attr)
                    pdf_link.data = '{0} | [pdf]'.format(self.arxiv_id)
                    paper_link.add_child(pdf_link)

                elif key == 'authors':
                    paper_authors = dom_node('paper-authors')
                    authors_string = ''
                    for author in self.info[key]:
                        authors_string += author + ', '
                    authors_string = authors_string[:-2]
                    paper_authors.data = authors_string

                elif key == 'comments':
                    paper_comments = dom_node('paper-comments')
                    paper_comments.data = self.info[key]

                elif key == 'subjects':
                    paper_subjects = dom_node('paper-subjects')
                    paper_subjects.data = self.info[key]

                elif key == 'abstract':
                    paper_abstract = dom_node('paper-abstract')
                    paper_abstract.data = self.info[key]
        dom_tree.add_child(paper_title)
        dom_tree.add_child(paper_link)
        dom_tree.add_child(paper_authors)
        dom_tree.add_child(paper_abstract)
        dom_tree.add_child(paper_comments)
        dom_tree.add_child(paper_subjects)
        html = dom_tree.to_string()
        return html

    def download_abstract(self, forcemode=False):
        if not forcemode:
            if self.info['abstract'] is not None:
                # print('skipping download abstract since already downloaded')
                return;
        r = requests.get('https://arxiv.org/abs/' + self.arxiv_id)
        parser = simple_parser()
        parser.feed(r.text)
        tree = parser.root
        meta_nodes = tree.search('meta')
        for meta_node in meta_nodes:
            meta_attr = meta_node.attributes
            if 'property' in meta_attr:
                if meta_attr['property'] == 'og:description':
                    self.info['abstract'] = utils.formal_text(meta_attr['content'])
                    return;

class arxiv_list_parser():
    def __init__(self, html_page):
        self.html_page = html_page
        self.parser = simple_parser()
        self.parser.feed(html_page)
        self.tree = self.parser.root

    def get_arxiv_id(self, dt_node):
        if len(dt_node.childs) == 0:
            return None
        else:
            arxiv_id = dt_node.childs[1].childs[0].attributes['href']
            arxiv_id = arxiv_id.split('/')[-1]
            return arxiv_id

    def get_paper_info(self, dd_node):
        title = None
        authors = []
        comments = None
        subjects = None
        if len(dd_node.childs) == 0:
            return None
        else:
            elements = dd_node.childs[0].childs
            for element in elements:
                if 'class' in element.attributes:
                    element_class = element.attributes['class']
                    if element_class == 'list-title mathjax':
                        title = utils.formal_text(element.data)
                    elif element_class == 'list-authors':
                        for child in element.childs:
                            if child.name == 'a':
                                authors.append(utils.formal_text(child.data))
                    elif element_class == 'list-comments mathjax':
                        comments = utils.formal_text(element.data)
                    elif element_class == 'list-subjects':
                        subjects = utils.formal_text(element.data)
        paper_info = {
            'title':title,
            'authors':authors,
            'comments':comments,
            'subjects':subjects,
            'abstract':None
        }
        return paper_info

    def get_papers(self):
        dts = self.tree.search('dt')
        dds = self.tree.search('dd')
        papers = []
        for dt, dd in zip(dts, dds):
            arxiv_id = self.get_arxiv_id(dt)
            if arxiv_id == None:
                continue;
            paper_info = self.get_paper_info(dd)
            if paper_info == None:
                continue;
            paper = arxiv_paper(arxiv_id, paper_info)
            papers.append(paper)
        return papers

    def get_paper_num(self):
        totally_paper_node = self.tree.search('small')[0].data
        total_num_split = totally_paper_node.split(' ')
        num_total = 0
        for split in total_num_split:
            if split.isdigit():
                num_total = int(split)
                break;
        return num_total

    def get_recent_info(self):
        # get each day start id and day_name
        day_name = []
        day_start = []
        li_nodes = self.tree.search('ul')[0].childs
        for li in li_nodes:
            link = li.childs[0].attributes['href']
            start = None
            if link.find('#item') != -1:
                start = link.split('#')[-1][4:]
            else:
                start = link.split('=')[-2].split('&')[0]
            day_name.append(li.childs[0].data)
            day_start.append(int(start))
        # get total paper num
        num_total = self.get_paper_num()
        # get each day num.
        num_days = len(day_start)
        day_num = []
        for i in range(num_days):
            if i < num_days - 1:
                day_num.append(day_start[i+1] - day_start[i])
            else:
                day_num.append(num_total - day_start[i])

        # generate final info.
        recent_papers_info = {}
        for day, start, num in zip(day_name, day_start, day_num):
            current_day_info = {}
            current_day_info['start'] = start
            current_day_info['num'] = num
            recent_papers_info[day] = current_day_info
        return recent_papers_info

class arxiv_spider():
    def __init__(self, topic, arxiv_url = 'https://arxiv.org'):
        self.link = arxiv_url
        self.topic = topic
        self.base_url = self.link + '/list/' + self.topic


    def get_yearly_papers(self, year, log=False):
        yearly_url = self.base_url + '/' + year
        if log:
            print('visiting url [{0}] for basic information'.format(yearly_url))
        r = requests.get(yearly_url)
        list_parser = arxiv_list_parser(r.text)
        total_num = list_parser.get_paper_num()
        print('Total Number for this year:', total_num)
        yearly_url_all = yearly_url + '?skip={0}&show={1}'.format(0, total_num)
        if log:
            print('visiting url [{0}] for all papers'.format(yearly_url_all))
        r = requests.get(yearly_url_all)
        list_parser = arxiv_list_parser(r.text)
        yearly_papers = list_parser.get_papers()
        return yearly_papers

    # papers:
    # papers = {
    #     'key is day string': [content is a list of arxiv_paper class]
    # }

    def get_papers_on_search_list(self, search_url, log=True):
        if log:
            print('visiting url [{0}] for today papers.'.format(search_url))
        search_content = requests.get(search_url)
        search_content = search_content.text
        parser = simple_parser()
        parser.feed(search_content)
        tree = parser.root
        paper_nodes = tree.search('entry')
        print('num_searched_nodes:', len(paper_nodes))
        papers = []
        for node in paper_nodes:
            arxiv_id = node.search('id')[0].data.split('/')[-1]
            title = node.search('title')[0].data
            author_nodes = node.search('name')
            authors = [item.data for item in author_nodes]
            category_nodes = node.search('category')
            categories = [item.attributes['term'] for item in category_nodes]
            subjects = ''
            for cat in categories:
                subjects += cat + ','
            subjects = subjects[:-1]
            comments_node = node.search('arxiv:comment')
            if len(comments_node) == 0:
                comments = ''
            else:
                comments = node.search('arxiv:comment')[0].data
            abstract = node.search('summary')[0].data

            title = utils.formal_text(title)
            subjects = utils.formal_text(subjects)
            comments = utils.formal_text(comments)
            abstract = utils.formal_text(abstract)


            paper_info = {
            'title':title,
            'authors':authors,
            'comments':comments,
            'subjects':subjects,
            'abstract':abstract
            }

            paper = arxiv_paper(arxiv_id, paper_info)
            papers.append(paper)
        return papers

    def get_papers_by_ids(self, ids, log=True):
        num_groups = int((len(ids) + 9.1)/10)
        if log:
            print('spliting into {0} groups.'.format(num_groups))
        papers = []
        for i in range(num_groups):
            this_batch = ids[i * 10:(i+1)*10]
            id_list = ''
            for paper_id in this_batch:
                id_list += paper_id + ','
            id_list = id_list[:-1]
            search_url = 'http://export.arxiv.org/api/query?id_list=' + id_list
            batch_papers = self.get_papers_on_search_list(search_url, log)
            papers += batch_papers
        return papers


    def get_today_ids(self, log=True):
        rss_url = 'http://export.arxiv.org/rss/{0}'.format(self.topic)
        if log:
            print('visiting url [{0}] for today papers id.'.format(rss_url))
        rss_content = requests.get(rss_url)
        rss_content = rss_content.text
        parser = simple_parser()
        parser.feed(rss_content)
        rss = parser.root
        id_nodes = rss.search('rdf:li')
        paper_ids = []
        for node in id_nodes:
            paper_link = node.attributes['rdf:resource']
            paper_id = paper_link.split('/')[-1]
            paper_ids.append(paper_id)
        print('num_paper_ids:', len(paper_ids))
        return paper_ids

    def get_today_paper(self, return_day_name=False, log=True):
        today_ids = self.get_today_ids(log)
        papers = self.get_papers_by_ids(today_ids)
        print('num of papers:', len(papers))
        return papers



    def get_today_paper_backup(self, return_day_name=False):
        papers = self.get_recent_papers(recent_days=[1])
        today = None
        paper = None
        for day in papers:
            today = day
            paper = papers[day]
        if return_day_name:
            return paper, today
        else:
            return paper


    def get_recent_papers(self, recent_days=[1, 2, 3, 4, 5], log=False):
        recent_url = self.base_url + '/recent'
        if log:
            print('visiting url [{0}] for basic information'.format(recent_url))
        r = requests.get(recent_url)
        list_parser = arxiv_list_parser(r.text)
        recent_papers_info = list_parser.get_recent_info()
        print('paper info:', recent_papers_info)

        day_id = 1
        papers = {}
        for day in recent_papers_info:
            if day_id in recent_days:
                today_start = recent_papers_info[day]['start']
                today_num = recent_papers_info[day]['num']
                page_url = '/pastweek?skip={0}&show={1}'.format(today_start, today_num)
                day_url = self.base_url + page_url
                if log:
                    print('visiting url [{0}] for paper on day {1}'.format(day_url, day))
                r = requests.get(day_url)
                list_parser = arxiv_list_parser(r.text)
                today_papers = list_parser.get_papers()
                papers[day] = today_papers
            day_id += 1
        return papers
