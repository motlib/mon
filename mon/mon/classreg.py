'''Class registry for data collectors.'''

import inspect
import logging


class ClassRegistry():
    def __init__(self):
        self._classes = []

        
    def find_classes(self, module, baseclass):
        '''Find all classes in module and sub-modules, which are derived from 
        baseclass and register these classes.'''
        
        result = []

        self._find_classes(result, module, baseclass)
        
        for cls in result:
            self.register_class(cls)
        
        msg = 'Located {0} implementations: {1}'
        names = ', '.join(c.__name__ for c in result)
        logging.info(msg.format(len(result), names))


                
    def _find_classes(self, result, module, baseclass):
        '''Internal implementation to find classes derived from baseclass in 
        module and sub-modules. All found classes are added to the result 
        list.'''
        
        # find classes in module, which are subclasses of CollectorBase, but not
        # CollectorBase itself
        classes = inspect.getmembers(
            module,
            lambda x: (
                inspect.isclass(x)
                and issubclass(x, baseclass)
                and (x != baseclass)))
    
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
        '''Register a new class to be handled in the registry.'''
        
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
        '''Create instance of a collector class and add it to the internal 
        instances list for this class.
    
        :param cls: The class to instanciate.
        :param cfg: The config to pass to the constructur when creating the 
          instance.
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
        '''Create one instance for each registered class.

        :param cfg: A dictionary classname -> cfg. Each cfg is passed to the 
          constructor of the corresponding class.'''
        
        all_classes = [c['class'] for c in self._classes]

        for clsinfo in self._classes:
            # try to get the config. If not available, use empty dict.
            clscfg = cfg.get(clsinfo['fullname'], {})
            
            self.create_instance(clsinfo['class'], clscfg)

            
    def get_all_instances(self):
        '''Return an interator over all created instances of all classs.'''
        
        for clsinfo in self._classes:
            for inst in clsinfo['instances']:
                yield inst


    def get_instance_by_class(self, cls, only_one=True):
        clsinfo = self._get_class_info(cls)

        if only_one:
            if len(clsinfo['instances']) > 0:
                return clsinfo['instances'][0]
            else:
                return None
        else:
            return clsinfo['instances']
        
