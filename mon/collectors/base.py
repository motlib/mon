from datetime import datetime, timedelta
import logging
from socket import getfqdn
from subprocess import check_output

class CollectorBase():
    def __init__(self, cfg, interval=None):
        self._cfg = cfg

        if 'interval' in cfg:
            self._interval = cfg['interval']
        elif interval != None:
            self._interval = interval
        else:
            self._interval = 30
            
        self._next_run = datetime.now()

        # this will raise exceptions, if the collector requirements are not
        # fullfilled.
        self.check()


    def check(self):
        # this function can be overridden to check if all preconditions for this
        # collector are fullfilled to be used. E.g. check if commands are available
        pass

        
    def is_ready(self):
        return self._next_run < datetime.now()

    
    def get_next_run(self):
        return self._next_run

    
    def get_interval(self):
        return self._interval

    
    def get_data(self):
        topic = self._cfg.get('topic', self.__class__.__name__)
        values = self._get_values()

        self._next_run = (self._next_run + timedelta(seconds=self._interval))
        
        return (topic, values)


    def _get_file_data(self, filename, firstline=False, as_lines=False):
        '''Read contents of a file and return as string. If firstline is true, 
        only the first line of the file is returned.

        '''
        
        with open(filename, 'r') as f:
            if firstline:
                s = f.readline()
            else:
                s = f.read()

        if as_lines:
            return s.split('\n')
        else:
            return s

        
    def _get_cmd_data(self, cmd, firstline=False, as_lines=False):        
        output = check_output(cmd).decode('utf-8', errors='ignore')

        if firstline:
            return output.split('\n')[0]
        else:
            if as_lines:
                return output.split('\n')
            else:
                return output
