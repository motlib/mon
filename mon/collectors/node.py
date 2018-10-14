from mon.classreg import register_collector_class
from mon.collectors.base import CollectorBase
import mon.__version__

class NodeInfo(CollectorBase):
    def __init__(self, cfg):
        super().__init__(
            cfg=cfg,
            interval=3600)

    def _get_info(self, state):
        return {
            'mon_version': mon.__version__.__version__,
            'state': state,
        }

        
    def _get_values(self):
        return self._get_info('online')

register_collector_class(NodeInfo)
