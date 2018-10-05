
classes = {}

def register_collector_class(cls):
    classes[cls.__module__ + '.' + cls.__name__] = cls
    print('Collector Class', cls, cls.__name__)

def create_collector_instance(clsname, **params):
    if clsname not in classes:
        raise KeyError('Requested collector class {0} not available.'.format(clsname))

    cls = classes[clsname]

    return cls(**params)
