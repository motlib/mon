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
            namespace='cpu')

        
    def _get_values(self):
        pattern = '/sys/class/thermal/thermal_zone*/temp'

        files = glob.iglob(pattern)

        data = {}
        for filename in files: 
            temp = int(self._get_file_data(filename, firstline=True)) / 1000.0
            zone = filename.split('/')[4]

            data[zone] = temp

        return {'temp': data}

register_collector_class(CpuTemp)


class LsCpuInfoInterface(CollectorBase):
    def _get_cpuinfo(self):
        output = self._get_cmd_data(['lscpu'], as_lines=True)

        data = {}
        for line in output:
            m = re.match(r'^([^:]+):\s+(.*)$', line)

            if m:
                data[m.group(1)] = m.group(2)
                
        return data
    


class CpuInfo(LsCpuInfoInterface):
    '''Collect basic information about the CPUs.'''
    
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=3600,
            namespace='cpu')

        
    def check(self):
        self._get_cmd_data(['lscpu'])
        
        
    def _get_values(self):
        data = self._get_cpuinfo()

        result = {
            'cores': data.get('CPU(s)', 'n/a'),
            'architecture': data.get('Architecture', 'n/a'),
        }

        return { 'cpuinfo': result }
            
register_collector_class(CpuInfo)


class CpuFrequency(LsCpuInfoInterface):
    '''Collect basic information about the CPUs.'''
    
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=30,
            namespace='cpu')

        
    def check(self):
        cpuinfo = self._get_cpuinfo()
        if 'CPU MHz' not in cpuinfo:
            raise Exception('Architecture does not support CPU frequency reporting by lscpu.')


    def _get_values(self):
        data = self._get_cpuinfo()

        return { 'cpu_frequency': data['CPU MHz'] }
            
register_collector_class(CpuFrequency)
