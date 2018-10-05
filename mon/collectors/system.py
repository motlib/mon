
from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase
        
class LoadAvg(CollectorBase):
    def __init__(self, cfg):
        super().__init__(cfg)

        self._interval = 3

        
    def get_namespace(self):
        return '/system'

    
    def get_values(self):
        with open('/proc/loadavg', 'r') as f:
            loaddata = f.readline()

        keys = ('loadavg_1', 'loadavg_5', 'loadavg_15')
        values = (float(v) for v in loaddata.split(' ')[0:3])

        return dict(zip(keys,values))


    
register_collector_class(LoadAvg)
