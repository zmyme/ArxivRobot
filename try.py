import arxiv_service
import time

now = arxiv_service.cron_time(time.localtime(time.time()))
# now.show()
# while True:
# 	now.next_day()
# 	now.show()

# running time
# minute hour day month week year
# * means always.
# a-b means from a to b (a and b included)
# a means run at this time.
# must match all to execute a command.

schedule = arxiv_service.cron_expr('0 0 29 2 * *')
for i in range(10):
	now = schedule.next_run(now)
	now.show()
	print(now.to_struct_time())