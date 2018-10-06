import logging


classes = {}


def register_collector_class(cls):
    clsname = cls.__module__ + '.' + cls.__name__
    classes[clsname] = cls

    msg = "Registered collector class '{clsname}'."
    logging.debug(msg.format(clsname=clsname))

    
def create_collector_instance(clsname, **params):
    if clsname not in classes:
        raise KeyError('Requested collector class {0} not available.'.format(clsname))

    cls = classes[clsname]

    return cls(**params)


def create_collectors(colcfg):
    collectors = []
    
    for cfg in colcfg:
        inst = create_collector_instance(
            clsname=cfg['class'],
            cfg=cfg)
        collectors.append(inst)

    return collectors


def create_all_collectors():
    collectors = []
    for clsname in classes.keys():
        collectors.append(create_collector_instance(clsname, cfg=dict()))

    return collectors
