from datetime import datetime, timedelta
import logging
from socket import getfqdn
from subprocess import check_output

class CollectorBase():
    def __init__(self, cfg, interval=None, namespace=''):
        self._cfg = cfg

        if 'interval' in cfg:
            self._interval = cfg['interval']
        elif interval != None:
            self._interval = interval
        else:
            self._interval = 30

        if namespace != '' and not namespace.endswith('/'):
            namespace += '/'
        self._ns = namespace
            
        self._next_run = datetime.now()

        try:
            self.check()
        except Exception as e:
            msg = "Requirements for collector '{0}' are not fulfilled: {1}"
            logging.error(msg.format(
                self.__class__.__name__,
                e))


    def check(self):
        # this function can be overridden to check if all preconditions for this
        # collector are fullfilled to be used. E.g. check if commands are available
        pass

        
    def is_ready(self):
        return self._next_run < datetime.now()

    
    def get_next_run(self):
        return self._next_run

    
    def get_data(self):
        values = self._get_values()

        # prepend prefix to all value keys
        data = {self._ns + k: v for k,v in values.items()}

        self._next_run = (self._next_run + timedelta(seconds=self._interval))
        
        return data


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
