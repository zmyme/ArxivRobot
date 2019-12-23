from lib.parser import dom_node, simple_parser
from lib import parser
from lib import utils
import os
import config

import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email.header import Header
from email import generator
def send_mail(reciver, title, content):

        # with open('email.html', 'w', encoding="utf-8") as f:
        #       f.write(content)
        # 20:24

        username = config.username
        password = config.password
        replyto = config.replyto
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(title)
        msg['From'] = '%s <%s>' % (Header(config.sender_name), username)
        msg['To'] = reciver
        msg['Reply-to'] = replyto
        msg['Message-id'] = email.utils.make_msgid()
        msg['Date'] = email.utils.formatdate()
        texthtml = MIMEText(content, _subtype='html', _charset='UTF-8')
        msg.attach(texthtml)

        # with open('email.eml', 'w') as outfile:
        #     gen = generator.Generator(outfile)
        #     gen.flatten(msg)

        try:
            client = smtplib.SMTP_SSL(config.smtp_ssl_addr)
            # client.connect('smtpdm-ap-southeast-1.aliyun.com', 80)
            client.set_debuglevel(0)
            client.login(username, password)
            client.sendmail(username, reciver, msg.as_string())

            client.quit()
            print ('Email send to {0} success!'.format(reciver))
            return True
        except smtplib.SMTPConnectError as e:
            print ('Connection Error:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPAuthenticationError as e:
            print ('Authentication Error:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPSenderRefused as e:
            print ('Sender Refused:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPRecipientsRefused as e:
            print ('SMTPRecipients Refused:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPDataError as e:
            print ('Data Error:', e.smtp_code, e.smtp_error)
        except smtplib.SMTPException as e:
            print ('SMTPException:', e.message)
        except Exception as e:
            print ('Unknown error:', str(e))
        return True

class arxiv_emailer():
    def __init__(self, arxiv_bot, feeds_generator, session_file = './config/email_session.xml', debug=False):
        self.debug = debug
        self.email_info = dom_node()
        self.session_file = session_file
        self.sessions = None
        if self.session_file is not None:
                self.load_session()

        self.bot = arxiv_bot
        self.feeds = feeds_generator

    def send_daily_email(self):
        emails = self.feeds.generate_daily_emails()
        today = utils.str_day()
        for name in emails:
            email = emails[name]
            send = False
            if name not in self.sessions:
                print('New user found!')
                self.sessions[name] = {}
                self.sessions[name]['last-send'] = today
                send = True

            if self.sessions[name]['last-send'] != today:
                send = True

            if send:
                print('Sending email to user {0} [{1}]'.format(name, email['reciver']))
                print('reciver:', email['reciver'])
                print('title:', email['title'])
                print('content:', len(email['content']))
                success = False
                if not self.debug:
                        success = send_mail(email['reciver'], email['title'], email['content'])
                if success:
                    self.sessions[name]['last-send'] = today
                self.save_session()
            else:
                print('skipping user {0} since already sent!'.format(name))

    def load_session(self, session_file=None):
        if session_file is None:
            session_file = self.session_file
        tree = None
        with open(session_file, 'r') as f:
            xml = f.read()
            xmlparser = simple_parser()
            xmlparser.feed(xml)
            tree = xmlparser.root
        sessions = parser.dom2dict(tree)
        if 'root' in sessions:
            sessions = sessions['root']
        else:
            sessions = {}
        self.sessions = sessions
        print(self.sessions)
        return sessions

    def save_session(self, session_file=None):
        if session_file is None:
            session_file = self.session_file
        if session_file is None:
            return None
        xml = parser.dict2dom(self.sessions).to_string()
        with open(session_file, 'w') as f:
            f.write(xml)
        return xml

if __name__ == '__main__':
    emailer = arxiv_emailer(None, None, None)
    emailer.send_daily_email()
    print(emailer.load_session())
    print(emailer.save_session())
