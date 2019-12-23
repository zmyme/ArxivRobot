import sys

class VirtualScreen():
	def __init__(self, max_history=1000):
		self.max_history = max_history
		self.contents = []

	def write(self, message):
		self.contents.append(message)

	def last(self, line=10, output=sys.stdout):
		num_lines = len(self.contents)
		start_line = num_lines - line
		if start_line < 0:
			start_line = 0
		display = self.contents[start_line:]
		for line in display:
			output.write(line)
		output.write('\n')