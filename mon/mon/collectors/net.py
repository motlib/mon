from datetime import datetime
import re
import http.client
import platform
import subprocess

from mon.collectors.base import CollectorBase
from mon.utils import get_cmd_data, get_file_data


class NetDeviceInfo(CollectorBase):
    '''Collect network device statistics.'''
    
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=20)

        self._filter_devs = cfg['filter_devices'] if 'filter_devices' in cfg else ()
        
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

        devinfos = [
            self.get_dev_info(d)
            for d in self.get_devices()
            if d not in self._filter_devs]

        return {
            'devices': devinfos
        }


class ConnectivityInfo(CollectorBase):
    '''Check for internet / network connectivity.'''
    
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=120)

        self._check_functions = {
            'http': self.check_http,
            'ping': self.check_ping,
        }

        
    def check(self):
        pass


    def check_http(self, check):
        conn = http.client.HTTPConnection(
            host=check['host'],
            timeout=check.get('timeout', 5))
        try:
            conn.request('HEAD', check['path'])
            r = conn.getresponse()
            conn.close()
            return True
        except:
            conn.close()
            
        return False

        
    def check_ping(self, check):
        '''Returns True if host responds to a ping request.'''

        args = ['ping']
        if platform.system().lower()=="windows":
            args.extend(('-n', '1'))
            args.extend(('-w', str(check.get('timeout', 1) * 1000)))
        else:
            args.extend(('-c', '1'))
            args.extend(('-W', str(check.get('timeout', 1))))
        args.append(check['host'])

        need_sh = False if platform.system().lower()=="windows" else True
    
        exitcode = subprocess.call(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

        return exitcode == 0
        
    
    def _get_values(self):

        results = []
        
        for check in self._cfg.get('checks', []):
            result = dict(check)

            if check['type'] in self._check_functions:
                result['reachable'] = self._check_functions[check['type']](check)
            else:
                msg = "Check type '{0}' not supported."
                raise Exception(msg.format(check['type']))

            results.append(result)
            
        return {'checks': results}
