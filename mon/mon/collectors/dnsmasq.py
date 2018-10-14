#cachesize.bind, insertions.bind, evictions.bind, misses.bind, hits.bind, auth.bind and servers.bind
#dig +short chaos txt @opi2 cachesize.bind hits.bind servers.bind
#"10000"
#"11142"
#"1.0.0.1#53 16643 124" "8.8.4.4#53 33564 393" "1.1.1.1#53 15075 169" "8.8.8.8#53 51897 851"

from datetime import datetime

from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase


DNSMASQ_HOST='@localhost'

class DnsMasqDnsInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=60)

        
    def check(self):
        cmd = [
            # main dig command
            'dig', '+short', 'chaos', 'txt', '+tries=1', '+timeout=2',
            DNSMASQ_HOST, 
            # dnsmasq statistics to query
            'cachesize.bind',
        ]
        data = self._get_cmd_data(cmd, as_lines=True)
        if len(data) != 1:
            raise Exception("Dnsmasq does not provide statistics in the expected format. Output was: " + str(data))

        
    def _get_values(self):
        cmd = [
            # main dig command
            'dig', '+short', 'chaos', 'txt', '+tries=1', '+timeout=2',
            DNSMASQ_HOST, 
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
        lines = self._get_cmd_data(cmd, as_lines=True)

        #if len(data) != 7:
        #    raise Exception("Unexpected command output.")

        data = {
            'cachesize': int(lines[0].replace('"', '')),
            'insertions': int(lines[1].replace('"', '')),
            'evictions': int(lines[2].replace('"', '')),
            'misses': int(lines[3].replace('"', '')),
            'hits': int(lines[4].replace('"', '')),
            'auth': int(lines[5].replace('"', '')),
        }

        if data['hits'] + data['misses'] != 0:
            data['hitrate_pct'] = float(data['hits']) / (data['hits'] + data['misses']) * 100
        else:
            data['hitrate_pct'] = 0.0
        
        return data

register_collector_class(DnsMasqDnsInfo)


class DnsMasqDhcpInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=60)

        
    def check(self):
        data = self._get_file_data('/var/lib/misc/dnsmasq.leases', as_lines=True)


    def _get_values(self):
        # example line
        # 1539513512 02:42:a0:15:a2:c3 192.168.0.111 opi1 *

        data = self._get_file_data('/var/lib/misc/dnsmasq.leases', as_lines=True)

        leases = []
        
        for line in data:
            fields = line.split()
            if len(fields) < 4:
                continue

            exp_time = datetime.fromtimestamp(int(fields[0]))
            
            lease = {
                'expiration': exp_time.isoformat(),
                'hostname': fields[3],
                'ip': fields[2],
                'mac': fields[1],
            }

            leases.append(lease)

        return {'leases': leases}

register_collector_class(DnsMasqDhcpInfo)
