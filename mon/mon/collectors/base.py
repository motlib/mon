from datetime import datetime
import logging


class CollectorBase():
    def __init__(self, cfg, interval=None):
        self._cfg = cfg

        if 'interval' in cfg:
            self._interval = cfg['interval']
        elif interval != None:
            self._interval = interval
        else:
            self._interval = 30
            

        # this will raise exceptions, if the collector requirements are not
        # fullfilled.
        self.check()

        
    def get_interval(self):
        return self._interval
        

    def check(self):
        # this function can be overridden to check if all preconditions for this
        # collector are fullfilled to be used. E.g. check if commands are available
        pass

    
    def get_data(self):
        topic = self._cfg.get('topic', self.__class__.__name__)
        values = self._get_values()

        values['_class'] = self.__class__.__name__

        # JSON usually uses isoformat (generated by datetime.now().isoformat()),
        # but this cannot be converted back to datetime object with standard
        # python, so we use unix timestamps
        values['_timestamp'] = int(datetime.utcnow().timestamp())
        
        values['_interval'] = self.get_interval()
        
        return (topic, values)


