import arxiv_bot
import email_sender
import subscriber_utils
import feeds
from lib import utils
import os
from lib import service
from lib.console import console
from lib import screen

subscribe_manager = subscriber_utils.subscribe_manager()
# subscribe_manager.load()

bot = arxiv_bot.arxiv_bot(subscribe_manager.get_subscribed_topics())
feeds_generator = feeds.feed_manager(subscribe_manager, bot)
emailer = email_sender.arxiv_emailer(bot, feeds_generator, debug=False)

log_screen = screen.VirtualScreen()
manager = service.ServiceManager(output=log_screen)

daily_mail_service = service.service(
	emailer.send_daily_email,
	cron='0 4 * * 1-5',
	name = 'send daily email'
)
manager.add(daily_mail_service)

shell = console('ArxivBot')
def command_load(args):
	if args == 'subscriber':
		subscribe_manager.load()

shell.regist('load', command_load, help_info='load config. (only subscriber supported till now)')
service_shell = service.get_service_console(manager, 'ServiceManager')
shell.regist('service', service_shell, help_info='service mamager')

# cron time:
# min hour day month week
manager.start()
shell.interactive()
