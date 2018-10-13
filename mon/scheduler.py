from datetime import datetime
import logging
from time import sleep

class Scheduler():
    def __init__(self, tasks, work_fct):
        if len(tasks) == 0:
            raise ValueError('Cannot work on empty task list.')
        
        self._tasks = tasks
        self._work_fct = work_fct


    def _do_work(self):
        '''Process all tasks in ready state by running them through the work_fct.'''
        
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
    
            logging.debug(
                'Scheduler sleeping for {s:.2f}s'.format(s=sleep_time))
            
            sleep(max(sleep_time, 0))
