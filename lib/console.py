from . import utils
import os
import traceback

class console():
	def __init__(self, name='base'):
		self.name = name
		self.hint = '$ '
		self.exit_cmd = ['exit', 'quit', 'bye']
		self.exit_info = 'Bye~'
		self.commands = {}
		self.alias = {}
		self.warn_level = 4
		self.exit_flag = False
		self.debug = True
		self.platform = utils.detect_platform()
		self.is_child = False
		self.father = None

		self.regist_internal_command()

	def get_hint(self):
		if self.platform == 'Linux':
			hint = '\033[0;33m({0})\033[0;31m{1}\033[0m'.format(self.name, self.hint)
		else:
			hint = '({0}){1}'.format(self.name, self.hint)
		return hint

	def regist_internal_command(self):
		self.regist(
			'help',
			action=self.command_help,
			alias=['h'],
			help_info='display this help info.',
			kind='sys'
			)
		self.regist(
			'exit',
			action=self.command_exit_console,
			alias=['quit','bye'],
			help_info='exit current console.',
			kind='sys'
			)
		self.regist(
			'cls',
			action=self.command_clear_screen,
			alias=['clear', 'clc'],
			help_info='clear screen.',
			kind='sys'
			)
		self.regist(
			'alias',
			action=self.command_alias,
			help_info='display alias info or create new alias.',
			kind='sys'
			)
		self.regist(
			'os',
			action=self.command_os,
			help_info='run a system command.',
			kind='sys'
			)


	def translate_command(self, command):
		while command in self.alias and command not in self.commands:
			command = self.alias[command]
		return command

	def find_equal_command(self, command, ret_type = str, ignored = []):
		finished = []
		new = []

		cmds = [command]
		while len(finished) != len(cmds):
			# find child
			if command in self.alias:
				if self.alias[command] not in cmds:
					cmds.append(self.alias[command])
			# find fathers
			for al in self.alias:
				if self.alias[al] == command:
					if al not in cmds:
						cmds.append(al)
			# found finished.
			finished.append(command)
			for cmd in cmds:
				if cmd not in finished:
					command = cmd


		if ret_type is str:
			finished = utils.list2csv(finished)
		return finished



	def get_alias(self, command, ret_type=str):
		alias = []
		for al in self.alias:
			if self.alias[al] == command:
				alias.append(al)

		if ret_type is str:
			alias = utils.list2csv(alias)

		return alias

	def command_exist(self, command):
		if command in self.commands or command in self.alias:
			return True
		else:
			return False

	def add_alias(self, command, alias):
		if self.command_exist(alias):
			if warn_level >= 3:
				print('Alias {0} will not be added since already used'.format(al))
		else:
			self.alias[alias] = command

	# kind: standard or shared
	#	standard: help info will be displayed
	#	shared: help info will not be displayed in sub command.
	def regist(self, command, action, alias=None, help_info='no help provided.', kind='standard'):
		if type(action) == console:
			action.is_child = True
			action.father = self
		exist = self.command_exist(command)
		if exist:
			if self.warn_level >=3:
				print('Command {0} will not be added sinece already exist.'.format(command))
			return

		if type(alias) is list:
			for al in alias:
				self.add_alias(command, al)
		elif type(alias) is str:
			self.add_alias(command, alias)
		elif alias is None:
			pass
		else:
			if self.warn_level > 3:
				print('Unknown alias type, no alias will be added.')
		self.commands[command] = {}
		self.commands[command]['action'] = action
		self.commands[command]['help'] = help_info
		self.commands[command]['kind'] = kind

	def handle_command(self, command, args):
		if command in self.commands:
			act = self.commands[command]['action']
			try:
				act(args)
			except KeyboardInterrupt:
				pass
			except:
				print('Exception occured while processing command \"{0} {1}\".'.format(command, args))
				print('More information are shown below.\n', traceback.format_exc())
		else:
			print('Unknown command \"{0}\"'.format(command))

	# seperate command and its args.
	def parse_command(self, string):
		string += ' '
		length = len(string)
		command_end = 0
		parse_start = False
		for i in range(length):
			blank = utils.is_blank(string[i])
			if not blank:
				parse_start=True
			if parse_start and blank:
				command_end = i
				break

		command = string[:command_end]
		command = utils.remove_blank_in_endpoint(command)
		args = utils.remove_blank_in_endpoint(string[command_end:])
		return command, args

	def parse(self, string):
		command, args = self.parse_command(string)
		exitsted_commands = []
		while command in self.alias:
			if command not in exitsted_commands:
				exitsted_commands.append(command)
				command = self.alias[command]
				string = command + ' ' + args
				command, args = self.parse_command(string)
			else:
				break

		return command, args


	def show_help_info(self, command, prefix, indent, depth=0):
		command = self.translate_command(command)
		action = self.commands[command]['action']
		kind = self.commands[command]['kind']
		if kind == 'sys' and depth > 0:
			return
		alias = self.get_alias(command, ret_type=str)
		if alias != '':
			print('{0}{1}({2}):'.format(prefix, command, alias))
		else:
			print('{0}{1}:'.format(prefix, command))
		print('{0}{1}{2}'.format(prefix, indent, self.commands[command]['help']))
		if type(action) == console:
			action.command_help('', prefix=prefix+indent, indent=indent, depth=depth+1)

	def debug_log(self, command, args):
		if self.debug:
			print('command:[{0}] args:[{1}]'.format(command, args))

	def command_exit_console(self, args):
		if not self.is_child:
			print(self.exit_info)
		self.exit_flag = True

	def command_clear_screen(self, args):
		if self.platform == 'Windows':
			os.system('cls')
		elif self.platform == 'Linux':
			os.system('clear')
		return False

	def command_help(self, args, prefix = '', indent='    ', depth=0):
		command, args = self.parse_command(args)
		if command is not "":
			if self.command_exist(command):
				self.show_help_info(command, prefix, indent, depth)
			else:
				print('Unknown command \"{0}\"'.format(command))
		else:
			for command in self.commands:
				self.show_help_info(command, prefix, indent, depth)

	def command_alias(self, args):
		alias_parse = args.split('=')
		if len(alias_parse) == 2:
			alias = utils.remove_blank_in_endpoint(alias_parse[0])
			command = utils.remove_blank_in_endpoint(alias_parse[1])
			if command is not '':
				self.alias[alias]=command
			else:
				del self.alias[alias]
		elif args == '':
			for alias in self.alias:
				print('{0}={1}'.format(alias, self.alias[alias]))
		elif len(alias_parse) == 1:
			if args in self.alias:
				print('{0}={1}'.format(args, self.alias[args]))
				equal_alias = self.find_equal_command(args)
				if equal_alias != '':
					print('Hint: {0} are all equivalent.'.format(equal_alias))
			elif args in self.commands:
				als = self.get_alias(args, ret_type=str)
				if als == '':
					print('command {0} has no alias.'.format(args))
				else:
					print('command {0} is aliased as {1}'.format(args, als))
				equal_alias = self.find_equal_command(args)
				if equal_alias != '' and equal_alias != args:
					print('Hint: {0} are all equivalent.'.format(equal_alias))
			else:
				print('No alias \"{0}\" found.'.format(args))
		else:
			print('Syntax error, command not understood.')

	def command_os(self, args):
		if args == '':
			print('please specify os command')
		else:
			os.system(args)

	def execute(self, string):
		command, args = self.parse(string)
		if command is not "":
			self.handle_command(command, args)

	def __call__(self, args):
		if args != '':
			self.execute(args)
		else:
			self.exit_flag=False
			self.interactive()

	def interactive(self):
		while not self.exit_flag:
			try:
				input_str = input(self.get_hint())
				self.execute(input_str)
			except(KeyboardInterrupt):
				print('')


if __name__ == '__main__':
	con = console()
	con_sub = console()
	con_sub_sub = console()
	con_sub.regist('test_subsubcommand', con_sub_sub, alias='tss', help_info='A sub command.')
	con.regist('test_subcommand', con_sub, alias='ts', help_info='A sub command.')
	con.interactive()