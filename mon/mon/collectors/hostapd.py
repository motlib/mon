import re

from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase
from mon.utils import get_cmd_data


class HostapdInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=60)

        self._sta_pattern = r'^[a-f0-9]{2}(:[a-f0-9]{2}){5}$'
        self._sta_pattern_c = re.compile(self._sta_pattern)

        self._data_pattern = r'^(.*?)=(.*)$'
        self._data_pattern_c = re.compile(self._data_pattern)


    def check(self):
        # let's try to run hostapp_cli
        get_cmd_data(['hostapd_cli', 'all_sta'], as_lines=True)

        
    def _get_station_info(self):
        # Example output:
        # 10:41:7f:da:d0:85
        # flags=[AUTH][ASSOC][AUTHORIZED][SHORT_PREAMBLE][WMM]
        # aid=2
        # capability=0x431
        # listen_interval=20
        # supported_rates=82 84 8b 96 24 30 48 6c 0c 12 18 60
        # timeout_next=NULLFUNC POLL
        # dot11RSNAStatsSTAAddress=10:41:7f:da:d0:85
        # dot11RSNAStatsVersion=1
        # dot11RSNAStatsSelectedPairwiseCipher=00-0f-ac-4
        # dot11RSNAStatsTKIPLocalMICFailures=0
        # dot11RSNAStatsTKIPRemoteMICFailures=0
        # hostapdWPAPTKState=11
        # hostapdWPAPTKGroupState=0
        # rx_packets=231
        # tx_packets=160
        # rx_bytes=29119
        # tx_bytes=118030
        # connected_time=5
        
        lines = get_cmd_data(['hostapd_cli', 'all_sta'], as_lines=True)

        addr = None
        sdata = None
        all_data = []
        for line in lines:
            m = self._sta_pattern_c.match(line)
            if m:
                sdata = {'address': m.group(0)}
                all_data.append(sdata)

            m = self._data_pattern_c.match(line)
            if sdata and m:
                sdata[m.group(1)] = m.group(2)

        # fix data type of some integer values
        int_keys = (
            'rx_packets',
            'tx_packets',
            'rx_bytes',
            'tx_bytes',
            'connected_time'
        )
        
        for sta in all_data:
            try:
                for key in int_keys:
                    sta[key] = int(sta[key])
            except:
                pass
                
        return all_data

        
    def _get_values(self):
        return {
            'stations': self._get_station_info(),
        }

    
register_collector_class(HostapdInfo)
