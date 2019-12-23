import arxiv_bot
import feeds
import email_sender
import time
import subscriber_utils
import utils
from croniter import croniter
import threading

class test_service():
    def __init__(self, name):
        self.name = name
        pass

    def do(self):
        print('Job {0} run!'.format(self.name))

class mail_service():
    def __init__(self, emailer):
        self.emailer = emailer

    def do(self):
        self.emailer.send_daily_email()

class reload_subscriber():
    def __init__(self, subscriber_mgr):
        self.mgr = subscriber_mgr

    def do(self):
        self.mgr.load()

