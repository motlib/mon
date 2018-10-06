import logging


_classes = {}


def register_collector_class(cls):
    '''Register a collector class, so it can later be instanciated.'''
    
    clsname = cls.__module__ + '.' + cls.__name__
    _classes[clsname] = cls

    msg = "Registered collector class '{clsname}'."
    logging.debug(msg.format(clsname=clsname))

    
def _create__instance(clsname, **params):
    '''Create instance of a collector class.'''
    
    if clsname not in _classes:
        raise KeyError('Requested collector class {0} not available.'.format(clsname))

    cls = _classes[clsname]

    return cls(**params)


def create_collectors(colcfg, create_all=False):
    '''Create collector instances according to configuration.'''
    
    collectors = []

    # if specified, ensure that all collectors are used in config
    if create_all:
        for clsname in _classes.keys():
            if len([cfg for cfg in colcfg if cfg['class'] == clsname]) == 0:
                colcfg.append({'class': clsname})
    
    for cfg in colcfg:
        try:
            inst = _create__instance(
                clsname=cfg['class'],
                cfg=cfg)
            
            collectors.append(inst)
        except Exception as e:
            msg = "Failed to instanciate collector '{0}': {1}"
            
            logging.warning(msg.format(cfg['class'], e))

    return collectors
