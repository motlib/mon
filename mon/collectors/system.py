import socket

from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase
        
class LoadAvg(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=30,
            namespace='system')

        
    def _get_values(self):
        with open('/proc/loadavg', 'r') as f:
            loaddata = f.readline()

        loaddata = self._get_file_data(
            filename='/proc/loadavg',
            firstline=True)

        keys = ('loadavg_1', 'loadavg_5', 'loadavg_15')
        values = (float(v) for v in loaddata.split(' ')[0:3])

        return dict(zip(keys,values))

register_collector_class(LoadAvg)
    

class Uptime(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=60,
            namespace='system')


    def _get_values(self):
        data = self._get_file_data(
            filename='/proc/uptime',
            firstline=True)

        return {
            'uptime': float(data.split(' ')[0])
        }
        
register_collector_class(Uptime)


class HostInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=3600,
            namespace='')

    def _get_values(self):
        return {
            'hostname': socket.getfqdn(),
            'kernel_version': self._get_cmd_data(
                cmd=['uname', '-r'],
                firstline=True)
        }

register_collector_class(HostInfo)
