from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase
import mon.__version__

class NodeInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=3600)

        self._state = 'offline'

    def set_state(s):
        if not s in ('online', 'offline'):
            raise ValueError('Only online and offline are accepted.')

        self._state = s

                
    def _get_values(self):
        return {
            'mon_version': mon.__version__.__version__,
            'state': self._state,
        }

register_collector_class(NodeInfo)
