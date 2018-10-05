from datetime import datetime, timedelta
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


    def _get_file_data(self, filename, firstline=False):
        '''Read contents of a file and return as string. If firstline is true, 
        only the first line of the file is returned.

        '''
        
        with open(filename, 'r') as f:
            if firstline:
                return f.readline()
            else:
                return f.read()

            
    def _get_cmd_data(self, cmd, firstline=False):
        
        output = check_output(cmd).decode('utf-8', errors='ignore')
        
        if firstline:
            return output.split('\n')[0].strip()
        else:
            return output
