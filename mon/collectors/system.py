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
                firstline=True,as_lines=False)
        }

register_collector_class(HostInfo)


class MemoryInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=20,
            namespace='memory')

        
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


class StorageInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=60,
            namespace='storage')


    def _get_storage_info(self):
        data = self._get_cmd_data(['df', '-T'], as_lines=True)

        result = []
        
        # skip first line with heading
        for line in data[1:]:
            stinfo = {}

            # Expect 7 fields separated by multiple spaces.
            # /dev/sda1      ext4      28704676   5411692  21811820  20% /
            #m = re.match(
            #    r'([^ ]*)\s+([^ ]*)\s+([^ ]*)\s+([^ ]*)\s+([^ ]*)\s+([^ ]*)%\s+([^ ]*)',
            #    line)

            m = line.split()
            
            if m:
                stinfo = {
                    'device': m[0],
                    'type': m[1],
                    'size': int(m[2]),
                    'used': int(m[3]),
                    'free': int(m[4]),
                    'used_pct': float(m[3]) / float(m[2]) * 100,
                    'mount_point': m[6],
                }

                result.append(stinfo)
        
        return result
        

    def _get_values(self):
        stinfo = self._get_storage_info()

        ignore_fstypes = self._cfg.get('ignore_fstypes', ['tmpfs', 'devtmpfs'])

        stinfo = {s['mount_point'].replace('/', '_'):s
                  for s in stinfo
                  if s['type'] not in ignore_fstypes}

        return stinfo
        
register_collector_class(StorageInfo)
