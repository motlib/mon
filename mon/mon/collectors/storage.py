import re

from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase
from mon.utils import get_cmd_data

class StorageInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=60)


    def _get_storage_info(self):
        data = get_cmd_data(['df', '-T'], as_lines=True)

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

        stinfo = [s for s in stinfo if s['type'] not in ignore_fstypes]

        return {'filesystems': stinfo}
        
register_collector_class(StorageInfo)
