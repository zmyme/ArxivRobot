import requests
from html.parser import HTMLParser

# r = requests.get('https://arxiv.org/list/cs.CV/recent')
r = requests.get('https://arxiv.org/list/cs.CV/recent')
# r = requests.get('http://xxx.itp.ac.cn/list/cs.CV/recent')
# r = requests.get('https://arxiv.org/list/cs.CV/pastweek?skip=25&show=25')

# print(r.status_code)
print(r.text)
