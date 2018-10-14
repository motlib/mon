#cachesize.bind, insertions.bind, evictions.bind, misses.bind, hits.bind, auth.bind and servers.bind
#dig +short chaos txt @opi2 cachesize.bind hits.bind servers.bind
#"10000"
#"11142"
#"1.0.0.1#53 16643 124" "8.8.4.4#53 33564 393" "1.1.1.1#53 15075 169" "8.8.8.8#53 51897 851"

from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase


class DnsMasqInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=60)

        
    def check(self):
        cmd = [
            # main dig command
            'dig', '+short', 'chaos', 'txt', '+tries=1', '+timeout=2',
            '@localhost', 
            # dnsmasq statistics to query
            'cachesize.bind',
        ]
        data = self._get_cmd_data(cmd, as_lines=True)
        if len(data) != 1:
            raise Exception("Dnsmasq does not provide statistics in the expected format.")

        
    def _get_values(self):
        cmd = [
            # main dig command
            'dig', '+short', 'chaos', 'txt', '+tries=1', '+timeout=2',
            '@localhost', 
            # dnsmasq statistics to query
            'cachesize.bind',
            'insertions.bind',
            'evictions.bind',
            'misses.bind',
            'hits.bind',
            'auth.bind',
            # servers info does not yet get evaluated
            #'servers.bind'
        ]
        data = self._get_cmd_data(cmd, as_lines=True)

        if len(data) != 7:
            raise Exception("Unexpected command output.")

        data = {
            'cachesize': int(line[0].replace('"', '')),
            'insertions': int(line[1].replace('"', '')),
            'evictions': int(line[2].replace('"', '')),
            'misses': int(line[3].replace('"', '')),
            'hits': int(line[4].replace('"', '')),
            'auth': int(line[5].replace('"', '')),
        }
        
        return data

register_collector_class(DnsMasqInfo)
