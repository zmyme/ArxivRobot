import threading
import queue
import time

class Job():
    def __init__(self, func, args=[], kwargs={}, name=None):
        if name == None:
            name = 'job'
        self.id = None
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.results = None

    def run(self):
        self.results = self.func(*self.args, **self.kwargs)

    def set_name(self, name):
        self.name = name

    def set_id(self, jid):
        self.id = jid

    def __call__(self):
        self.run()

class Worker(threading.Thread):
    def __init__(self, work_queue, finished_queue):
        super(Worker, self).__init__()
        self.queue = work_queue
        self.finished = finished_queue
        self.terminate = False
        self.daemon=True

    def stop(self):
        self.terminate = True

    def run(self):
        while not self.terminate:
            try:
                task = self.queue.get(timeout=1)
                task.run()
                self.queue.task_done()
                self.finished.put(task)
            except queue.Empty:
                pass
            except KeyboardInterrupt:
                print("you stop the threading")

class ParallelHost():
    def __init__(self, num_threads=8):
        self.num_threads = num_threads
        self.workers = []
        self.tasks = queue.Queue()
        self.results = queue.Queue()
        self.rets = {}
        self.id = 0
        for i in range(self.num_threads):
            worker = Worker(self.tasks, self.results)
            self.workers.append(worker)
        for worker in self.workers:
            worker.start()

    def __del__(self):
        self.stop('kill')

    # soft stop: wait until all job done
    # hard stop: stop even with unfinished job
    # kill stop: whatever the thread is doing, exit.
    def stop(self, mode='soft'):
        print('Trying to stop.')
        if mode == 'soft':
            self.tasks.join()
            print('All job finished.')
        for worker in self.workers:
            worker.stop()
        if mode == 'kill':
            worker.join(0.01)

    def commit(self, job):
        self.id += 1
        job.set_id(self.id)
        self.tasks.put(job)
        return self.id

    def add_job(self, func, args=[], kwargs={}, name=None):
        job = Job(func, args, kwargs, name)
        return self.commit(job)

    def collect_all(self):
        while not self.results.empty():
            task = self.results.get()
            jid = task.id
            self.rets[jid] = task.results

    def get_result(self, jid, block=False):
        if jid in self.rets:
            ret = self.rets[jid]
            del self.rets[jid]
            return ret
        while True:
            if self.results.empty() and not block:
                break
            task = self.results.get()
            if task.jid == jid:
                return task.results
            else:
                self.rets[task.jid] = task.results

    def clear_results(self):
        while not self.results.empty():
            self.results.get()
        self.rets = {}

if __name__ == '__main__':
    host = ParallelHost()

    def loop_print(info, num):
        for i in range(num):
            print(info + ':' + str(i))
            time.sleep(1)

    for i in range(10):
        host.add_job(loop_print, ["loop_print_{0}".format(i), 5])

    host.terminate('kill')
