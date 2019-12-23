import time
import sys
import shlex
import argparse

from croniter import croniter
from . import utils
from . import parallel
from . import console
from . import screen
from . import utils

class service():
    def __init__(self, action, args=[], kwargs={}, cron='* * * * *', managed_output=False, name='service'):
        self.name = name
        self.action = action
        self.managed_output = managed_output
        self.args = args
        self.kwargs = kwargs
        self.output = sys.stdout
        self.last_result = None
        self.cronexpr = cron
        self.croniter = croniter(self.cronexpr, time.time())
        self.next_time = self.croniter.get_next()

    def run(self, daemon=None, dry=False):
        if not dry:
            self.next_time = self.croniter.get_next()

        new_args = []
        if self.managed_output:
            new_args = [self.output, *self.args]
        else:
            new_args = self.args
        if daemon is None:
            self.last_result = self.action(*new_args, **self.kwargs)
        else:
            daemon.add_job(self.action, new_args, self.kwargs, self.name)

class ServiceManager():
    def __init__(self, debug=False, output=sys.stdout):
        self.debug = debug
        self.services = {}
        self.deleted_services = {}
        self.protected_service = []
        self.daemon = parallel.ParallelHost()
        self.sid = 0
        self.terminate = False
        self.output = output

        self.set_refresh_time()

    def stop(self):
        self.daemon.stop()
        self.terminate = True

    def __del__(self):
        self.stop()

    def log(self, *args, end='\n'):
        self.output.write('[{0}]'.format(utils.str_time()))
        for arg in args:
            arg = str(arg)
            self.output.write(arg)
        self.output.write(end)

    def add(self, service, protected=False):
        self.sid += 1
        service.output = self.output
        self.services[self.sid] = service
        if protected:
            self.protected_service.append(self.sid)
        return self.sid

    def delete(self, sid):
        if sid in self.protected_service:
            self.log('Can not delete protected service.')
            return
        if sid in self.services:
            self.deleted_services[sid] = self.services[sid]
            del self.services[sid]
        else:
            self.log('The sid [{0}] do not exist!'.format(sid))

    def recover(self, sid):
        if sid in self.deleted_services:
            self.services[sid] = self.deleted_services[sid]
            del self.deleted_services[sid]
        else:
            self.log('The sid [{0}] is not found recycle bin.'.format(sid))

    def set_refresh_time(self, refresh_cron='* * * * *'):
        def refresh():
            pass
        refresh_service = service(refresh, cron=refresh_cron, name='refresh')
        self.add(refresh_service, protected = True)

    def get_next(self):
        next_sid = -1
        next_time = -1
        for sid in self.services:
            service = self.services[sid]
            if service.next_time < next_time or next_sid < 0:
                next_sid = sid
                next_time = service.next_time
        return next_sid, next_time

    def loop(self):
        while not self.terminate:
            next_sid, next_time = self.get_next()
            service = self.services[next_sid]
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.log('Running service {0} (SID={1})'.format(service.name, next_sid))
            if next_sid in self.services:
                service.run(self.daemon)
            else:
                self.log('the sheduled service wiil not run since it is canceled.')


    # mode: background: return immidietly
    #       foreground: stuck here.
    def start(self, mode='background'):
        if mode == 'background':
            self.daemon.add_job(self.loop, name='service main loop')
        else:
            self.loop()

def get_service_console(manager, name='service'):

    con = console.console(name)

    def command_show(args):
        print('Active services:')
        for sid in manager.services:
            print('SID: {0} | Name: {1}'.format(sid, manager.services[sid].name))
        print('Deleted services:')
        for sid in manager.deleted_services:
            print('SID: {0} | Name: {1}'.format(sid, manager.deleted_services[sid].name))

    def command_add(args):
        parser = argparse.ArgumentParser()
        parser.add_argument('cron', type=str, help='A cron expr')
        parser.add_argument('task', type=str, help='task to run, should be a valid command')
        parser.add_argument('--name', '-n', type=str, default='command service', help='name of the task')
        args = shlex.split(args)
        args = parser.parse_args(args)
        cron = args.cron
        if not croniter.is_valid(cron):
            print('Invalid cron expression.')
        task = args.task
        name = args.name
        service_to_add = service(con.execute, args=[task], cron=cron, name=name)
        manager.add(service_to_add)

    def command_delete(args):
        sid = None
        if args.isdigit():
            if int(args) in manager.services:
                sid = int(args)
        if sid is not None:
            manager.delete(sid)
        else:
            print('command arugment \"{0}\" is not understood.'.format(args))

    def command_recover(args):
        sid = None
        if args.isdigit():
            if int(args) in manager.deleted_services:
                sid = int(args)
        if sid is not None:
            manager.recover(sid)
        else:
            print('command arugment \"{0}\" is not understood.'.format(args))

    def command_run(args):
        sid = None
        if args.isdigit():
            if int(args) in manager.services:
                sid = int(args)
        if sid is not None:
            manager.services[sid].run(dry=True)
        else:
            print('command arugment \"{0}\" is not understood.'.format(args))

    def command_info(args):
        line = None
        if args != '':
            if args.isdigit():
                line = int(args)
        if line is None:
            line = 10
        manager.output.last(line)

    def command_next(args):
        next_sid, next_time = manager.get_next()
        info = ''
        indent = '    '
        info += 'Next Job: {0}'.format(manager.services[next_sid].name)
        info += '\n{0}SID: {1}'.format(indent, next_sid)
        info += '\n{0}Scheduled Running Time: {1}'.format(indent, utils.time2str(next_time))
        info += '\n{0}Remeaning Time: {1}s'.format(indent, utils.float2str(next_time-time.time()))
        print(info)

    con.regist('show', command_show, help_info='Show all services.', alias=['ls'])
    con.regist('run', command_run, help_info='Run a service.')
    con.regist('info', command_info, help_info='Display service output log.')
    con.regist('next', command_next, help_info='Next job to run.')
    con.regist('add', command_add, help_info='Register a command as service.')
    con.regist('delete', command_delete, help_info='Delete a service', alias=['del'])
    con.regist('recover', command_recover, help_info='Recover a service.')
    return con


if __name__ == '__main__':
    def func1(output):
        output.write('func1')

    def func2(output):
        output.write('func2')

    def add(a, b):
        print('{0} + {1} = {2}'.format(a, b, a+b))

    def command_add(args):
        numbers = args.split(' ')
        a = float(numbers[0])
        b = float(numbers[1])
        add(a, b)

    log_screen = screen.VirtualScreen()
    manager = ServiceManager(output=log_screen)
    test1 = service(func1, cron='* * * * *', name='test1', managed_output=True)
    test2 = service(func2, cron='* * * * *', name='test2', managed_output=True)
    manager.add(test1)
    manager.add(test2)
    manager.start('background')

    con = get_service_console(manager)
    master = console.console()
    master.regist('service', con, help_info='service console')
    master.regist('add', command_add, help_info='Add two numbers.')
    master.interactive()
