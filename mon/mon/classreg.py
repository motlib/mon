'''Class registry for data collectors.'''

import logging


_classes = {}


def register_collector_class(cls):
    '''Register a collector class, so it can later be instanciated.

    :param cls: The class to register.'''
    
    clsname = '.'.join((cls.__module__, cls.__name__))
    _classes[clsname] = cls

    msg = "Registered collector class '{clsname}'."
    logging.debug(msg.format(clsname=clsname))

    
def _create_instance(clsname, **params):
    '''Create instance of a collector class.

    :param clsname: The class name to instanciate.
    :param params: And further parameters to pass to the constructor.

    :return: The new instance.
    '''
    
    if clsname not in _classes:
        raise KeyError('Collector class {0} not available.'.format(clsname))

    cls = _classes[clsname]

    return cls(**params)


def create_collectors(colcfg, create_all=False):
    '''Create collector instances according to configuration. If a collector 
    raises an Exception during instanciation, it is not included in the returned 
    list.

    :param colcfg: The collector configurations.
    :param create_all: If set to True, all available collectors are created, 
        even if not specified in the configuration.

    :return: A list with all instanciated collectors.'''
    
    collectors = []

    # if specified, ensure that all collectors are used in config
    if create_all:
        for clsname in _classes.keys():
            if len([cfg for cfg in colcfg if cfg['class'] == clsname]) == 0:
                colcfg.append({'class': clsname})
    
    for cfg in colcfg:
        try:
            inst = _create_instance(
                clsname=cfg['class'],
                cfg=cfg)
            
            collectors.append(inst)
        except Exception as e:
            msg = "Failed to instanciate collector '{0}': {1}"
            
            logging.warning(msg.format(cfg['class'], e))

    return collectors
