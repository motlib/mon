import glob
import json
import re

from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase
            

class CpuInfo(CollectorBase):
    '''Get CPU (and other zones) temperature.'''
    
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=30,
            namespace='cpu')

        
    def check(self):
        self._get_cmd_data(['lscpu'])
        
        
    def _get_lscpuinfo(self):
        output = self._get_cmd_data(['lscpu'], as_lines=True)

        # currently not active, as json support in lscpu is quite new
        #output = self._get_cmd_data(['lscpu', '--json'])
        #data = json.loads(output)

        # Convert json structure. in json, the field names have a trailing
        # ':'. This is removed here, too.
        #data = {i['field'][:-1]: i['data'] for i in data['lscpu']}

        data = {}
        for line in output:
            m = re.match(r'^([^:]+):\s+(.*)$', line)

            if m:
                data[m.group(1)] = m.group(2)
                
        return data
        
    def _get_temperatures(self):
        pattern = '/sys/class/thermal/thermal_zone*/temp'

        files = glob.iglob(pattern)

        data = []
        for filename in sorted(files): 
            temp = int(self._get_file_data(filename, firstline=True)) / 1000.0

            data.append(temp)

        return data

    
    def _get_values(self):
        info = self._get_lscpuinfo()
        result = {}
        
        if 'CPU(s)' in info:
            result['cores'] = int(info['CPU(s)'])
        if 'Architecture' in info:
            result['architecture'] = info['Architecture']
        if 'CPU MHz' in info:
            result['frequency'] = float(info['CPU MHz'])

        if 'CPU min MHz' in info:
            result['min_frequency'] = float(info['CPU min MHz'])
        if 'CPU max MHz' in info:
            result['max_frequency'] = float(info['CPU max MHz'])
            
        result['zone_temperatures'] = self._get_temperatures()
            
        return result
    
register_collector_class(CpuInfo)
