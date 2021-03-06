from datetime import datetime, timedelta
import logging
from time import sleep


# number of times a task can fail in a row, before it is disabled.
TASK_MAX_FAIL_COUNT = 5


class TaskWrapper():
    # TODO: implement '__str__' function
    
    def __init__(self, taskobj, interval):
        self.task_object = taskobj
        self._interval = interval

        self._next_run = datetime.now()

        self.fail_count = 0

        # by default, all tasks are enabled
        self._enabled = True
        

    def is_ready(self):
        return self._enabled and (self._next_run <= datetime.now())

    
    def get_next_run(self):
        return self._next_run

    
    def set_next_run(self):
        self._next_run = (self._next_run + timedelta(seconds=self._interval))

        
    def set_enabled(self, val):
        self._enabled = val
        

        
class Scheduler():
    def __init__(self, work_fct):

        self._tasks = []
        
        self._work_fct = work_fct

        
    def add_task(self, task, interval):
        self._tasks.append(TaskWrapper(task, interval))

        
    def _run_ready_tasks(self):
        '''Process all tasks in ready state by running them through the
        work_fct.'''
        
        # find ready tasks and run them
        ready_tasks = (
            t
            for t in self._tasks
            if t.is_ready()
        )
        
        for task in ready_tasks:
            try:
                # run work function for task
                self._work_fct(task.task_object)

                # reset fail counter
                task.fail_count = 0
            except Exception as e:
                msg = "Failed to run task '{0}'."
                logging.exception(msg.format(task.task_object))

                # increase fail counter on exception
                if task.fail_count < TASK_MAX_FAIL_COUNT:
                    task.fail_count += 1
                else:
                    task.set_enabled(False)
                    
                    msg = "Disabling task '{0}', because it failed {1} times."
                    logging.error(msg.format(task, task.fail_count))
                
            task.set_next_run()

            
    def run(self):
        if len(self._tasks) == 0:
            raise ValueError('Cannot run scheduler with empty task list.')
        
        while True:
            self._run_ready_tasks()
            
            # find next ready time of the collectors
            next_run = min(t.get_next_run() for t in self._tasks)
    
            # we sleep additional 0.1 seconds to be sure the collector is ready 
            sleep_time = (next_run - datetime.now()).total_seconds() + .1
    
            logging.debug(
                'Scheduler sleeping for {s:.2f}s'.format(s=sleep_time))
            
            sleep(max(sleep_time, 0))
