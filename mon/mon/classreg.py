'''Class registry for data collectors.'''

import inspect
import logging

from  mon.collectors.base import CollectorBase

_classes = {}


class ClassRegistry():
    def __init__(self):
        # class name -> details
        self._classes = []

        
    def find_classes(self, module, baseclass):
        result = []

        self._find_classes(result, module, baseclass)
        
        for cls in result:
            self.register_class(cls)
        
        msg = 'Located {0} implementations: {1}'
        names = ', '.join(c.__name__ for c in result)
        logging.info(msg.format(len(result), names))


                
    def _find_classes(self, result, module, baseclass):
        # find classes in module, which are subclasses of CollectorBase, but not
        # CollectorBase itself
        classes = inspect.getmembers(
            module,
            lambda x: inspect.isclass(x) and issubclass(x, CollectorBase) and (x != CollectorBase))
    
        # Add the found classes to the result
        result.extend(cls for (name, cls) in classes)
    
        # find true sub-modules  (by default, getmembers() finds all imported
        # modules, also system modules like os, sys, ...)
        mods = inspect.getmembers(
            module,
            lambda m: inspect.ismodule(m) and m.__name__.startswith(module.__name__))
    
        # recursive call to find classes in sub-modules
        for name, mod in mods:
            self._find_classes(result, mod, baseclass)


    def register_class(self, cls):
        classinfo = {
            'class': cls,
            'fullname': cls.__module__ + '.' + cls.__name__,
            'instances': [],
        }
        self._classes.append(classinfo)


    def _get_class_info(self, cls=None):
        classes = [c for c in self._classes if c['class'] == cls]

        # otherwise the class is registered more than once
        assert(len(classes) <= 1)

        if len(classes) > 0:
            return classes[0]
        return None
        
    
    def create_instance(self, cls, cfg, errors='ignore'):
        '''Create instance of a collector class.
    
        :param clsname: The class name to instanciate.
        :param params: And further parameters to pass to the constructor.
    
        :return: The new instance.
        '''

        clsinfo = self._get_class_info(cls)

        if clsinfo == None:
            msg = 'Class {0} not available.'
            raise KeyError(msg.format(cls.__name__))
    
        cls = clsinfo['class']

        try:
            inst = cls(cfg)
            clsinfo['instances'].append(inst)
        except Exception as e:
            if errors != 'ignore':
                raise
            else:
                msg = ("During instanciation of '{0}' an exception was "
                       "raised, but ignored. No instance created. Error was: {1}")
                logging.info(msg.format(cls.__name__, e))


    def create_all_instances(self, cfg):
        all_classes = [c['class'] for c in self._classes]

        for clsinfo in self._classes:
            # try to get the config. If not available, use empty dict.
            clscfg = cfg.get(clsinfo['fullname'], {})
            
            self.create_instance(clsinfo['class'], clscfg)

            
    def get_all_instances(self):
        for clsinfo in self._classes:
            for inst in clsinfo['instances']:
                yield inst


            

#    def create_collectors(self, colcfg, create_all=False):
#        '''Create collector instances according to configuration. If a collector 
#        raises an Exception during instanciation, it is not included in the returned 
#        list.
#    
#        :param colcfg: The collector configurations.
#        :param create_all: If set to True, all available collectors are created, 
#            even if not specified in the configuration.
#    
#        :return: A list with all instanciated collectors.'''
#        
#        collectors = []
#    
#        # if specified, ensure that all collectors are used in config
#        if create_all:
#            for clsname in _classes.keys():
#                if len([cfg for cfg in colcfg if cfg['class'] == clsname]) == 0:
#                    colcfg.append({'class': clsname})
#        
#        for cfg in colcfg:
#            try:
#                inst = _create_instance(
#                    clsname=cfg['class'],
#                    cfg=cfg)
#                
#                collectors.append(inst)
#            except Exception as e:
#                msg = "Failed to instanciate collector '{0}': {1}"
#                
#                logging.warning(msg.format(cfg['class'], e))
#    
#        return collectors
#
