from datetime import datetime
from time import sleep

class Scheduler():
    def __init__(self, tasks, work_fct):
        self._tasks = tasks
        self._work_fct = work_fct


    def _do_work(self):
        # find ready tasks and run them
        ready_tasks = (t for t in self._tasks if t.is_ready())
        for t in ready_tasks:
            # FIXME: not so nice, as its not visible that tasks manage their own
            # next ready time
            self._work_fct(t)
        
        
    def run(self):
        while True:
            self._do_work()
            
            # find next ready time of the collectors
            next_run = min(t.get_next_run() for t in self._tasks)
    
            # we sleep additional 0.1 seconds to be sure the collector is ready 
            sleep_time = (next_run - datetime.now()).total_seconds() + .1
    
            print('sleeping', sleep_time)
            
            sleep(max(sleep_time, 0))
