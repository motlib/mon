import glob
import re

from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase


class CpuTemp(CollectorBase):
    '''Get CPU (and other zones) temperature.'''
    
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=30,
            namespace='')

        
    def _get_values(self):
        pattern = '/sys/class/thermal/thermal_zone*/temp'

        files = glob.iglob(pattern)

        data = {}
        for filename in files: 
            temp = int(self._get_file_data(filename, firstline=True)) / 1000.0
            zone = filename.split('/')[4]

            data[zone] = temp

        return {'cputemp': data}

register_collector_class(CpuTemp)


class CPUInfo(CollectorBase):
    '''Collect basic information about the CPUs.'''
    
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=30,
            namespace='')

        
    def check(self):
        self._get_cmd_data(['lscpu'])


    def _get_cpuinfo(self):
        output = self._get_cmd_data(['lscpu'], as_lines=True)

        data = {}
        for line in output:
            m = re.match(r'^([^:]+):\s+(.*)$', line)

            if m:
                data[m.group(1)] = m.group(2)
                
        return data
        
    def _get_values(self):
        data = self._get_cpuinfo()

        result = {
            'cores': data.get('CPU(s)', 'n/a'),
            'architecture': data.get('Architecture', 'n/a'),
            'frequency': data.get('CPU MHz', 'n/a'),
            }

        return { 'cpuinfo': result }
            
register_collector_class(CPUInfo)
