from datetime import datetime, timedelta

class CollectorBase():
    def __init__(self, cfg):
        self._cfg = cfg

        # 30s is default. Can and shall be reset in derived class constructor
        self._interval = 30

        self._next_run = datetime.now()

        
    def get_interval(self):
        if 'interval' in self._cfg:
            return self._cfg['interval']
        else:
            return self._interval

        
    def get_namespace(self):
        return ''

    
    def is_ready(self):
        return self._next_run < datetime.now()

    
    def get_next_run(self):
        return self._next_run
    
    
    def get_data(self):
        values = self.get_values()
        ns = self.get_namespace()

        # prepend namespace name to all value keys
        data = {ns + '/' + k: v for k,v in values.items()}

        self._next_run = self._next_run + timedelta(seconds=self.get_interval())
        
        return data

    
