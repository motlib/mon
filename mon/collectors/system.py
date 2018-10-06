import re
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


class MemoryInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=20,
            namespace='system')

        
    def _get_meminfo(self):
        lines = self._get_file_data(
            filename='/proc/meminfo').split('\n')

        meminfo = {}
        
        for line in lines:
            m = re.match('^([^:]+):\s*(\d+)( kB)?$', line)
            if m:
                meminfo[m.group(1)] = int(m.group(2))

        return meminfo

    
    def _get_values(self):
        meminfo = self._get_meminfo()
        
        # Calculation according to htop author:
        # http://stackoverflow.com/questions/41224738/how-to-calculate-
        #  memory-usage-from-proc-meminfo-like-htop

        data = {}
        
        # All the memory used by the system.
        data['totalUsed'] = (meminfo['MemTotal'] - meminfo['MemFree']);

        # The memory the system can release whenever necessary and uses for
        # caching.
        data['cached'] = (
            meminfo['Cached'] + meminfo['SReclaimable'] - meminfo ['Shmem'])

        # Memory actually in use by processes. 
        data['inUse'] = (
            data['totalUsed'] - meminfo['Buffers'] - data['cached'])

        # Percent of memory used.
        data['pctInUse'] = float(data['inUse']) / meminfo['MemTotal']
        
        return data;

register_collector_class(MemoryInfo)
