
from datetime import datetime
import re

from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase
from mon.utils import get_cmd_data, get_file_data


class NetDeviceInfo(CollectorBase):
    '''Collect network device statistics.'''
    
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=20)

        self.rates = {}

        
    def check(self):
        #get_cmd_data(['lscpu'])
        pass
        

    def get_devices(self):
        cmd = ['ls', '-1', '/sys/class/net']

        devices = get_cmd_data(cmd, as_lines=True)

        return [d.strip() for d in devices if d.strip()!='']
        

    def _get_dev_dataflow(self, dev):
        rx = int(get_file_data(
            "/sys/class/net/{dev}/statistics/rx_bytes".format(dev=dev),
            firstline=True).strip())
        tx = int(get_file_data(
            "/sys/class/net/{dev}/statistics/tx_bytes".format(dev=dev),
            firstline=True).strip())

        return {
            'rx_bytes': rx,
            'tx_bytes': tx,
            'rx_rate': self._get_rate(dev + '_rx', rx),
            'tx_rate': self._get_rate(dev + '_tx', tx),
        }

    
    def get_dev_info(self, dev):
        '''Get network device info.
    
        :param dev: Network device name, e.g. eth0.
        :return: Dict with device info.'''
    
        devinfo = {
            'device': dev
        }
    
        # Example:
        # 2: ens160    inet 10.180.2.190/24 brd 10.180.2.255 scope global ens160 ...
        data = get_cmd_data(
            ['ip','-o','-4', 'address', 'show', dev],
            firstline=True)
        data = data.strip()
        
        m = re.search(r'inet ([.0-9]+)\/([0-9]+)', data)
            
        if m:
            devinfo['ipaddress'] = m.group(1)
            devinfo['netsize'] = int(m.group(2))

        # Example:
        # wlp3s0    inet6 fe80::6267:20ff:fe3c:14e8/64 scope link ...
        data = get_cmd_data(
            ['ip','-o','-6', 'address', 'show', dev],
            firstline=True)
        data = data.strip()
        
        m = re.search(r'inet6 ([0-9a-f:]+)\/([0-9]+)', data)
            
        if m:
            devinfo['ipv6address'] = m.group(1)
            devinfo['ipv6prefix'] = int(m.group(2))
            
        devinfo['hwaddress'] = get_file_data(
            "/sys/class/net/{dev}/address".format(dev=dev),
            firstline=True).strip()

        devinfo.update(self._get_dev_dataflow(dev))
        
        return devinfo


    def _get_values(self):
        devs = self.get_devices()

        devinfos = [self.get_dev_info(d) for d in self.get_devices()]

        return {
            'devices': devinfos
        }

register_collector_class(NetDeviceInfo)
