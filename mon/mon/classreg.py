'''Class registry for any kind of plug-in system.'''

import inspect
import logging
from pprint import pprint

class ClassRegistry():
    '''Class registry for any kind of plug-in system.'''


    def __init__(self):
        self._classes = []

        
    def find_classes(self, module, baseclass):
        '''Find all classes in module and sub-modules, which are derived from 
        baseclass and register these classes.

        :param module: The module where to start searching for classes.

        :param baseclass: Only find classes derived from baseclass, i..e. 
          classes are deteced, if they inherit directly or indirectly from this 
          baseclass.'''
        
        count = 0
        for cls in self._find_classes(module, baseclass):
            self.register_class(cls)
            count += 1

        msg = 'Located and registrered {0} classes'
        logging.debug(msg.format(count))


    def _find_classes(self, module, baseclass):
        '''Internal implementation to find classes derived from baseclass in 
        module and sub-modules. All found classes are added to the result 
        list.'''

        modules = [module]

        while len(modules) > 0:
            mod = modules.pop()

            # find classes in module, which are subclasses of baseclass, but
            # not baseclass itself
            classes = inspect.getmembers(
                mod,
                lambda x: (
                    inspect.isclass(x)
                    and issubclass(x, baseclass)
                    and (x != baseclass)
                )
            )

            for (name, cls) in classes:
                yield cls
            
            # find true sub-modules  (by default, getmembers() finds all imported
            # modules, also system modules like os, sys, ...)
            submods = inspect.getmembers(
                mod,
                lambda m: (
                    inspect.ismodule(m)
                    and m.__name__.startswith(module.__name__)))

            modules.extend(mod for (name,mod) in submods)
    

    def register_class(self, cls):
        '''Register a new class to be handled in the registry.

        :param cls: The class (type object) to register'''
        
        classinfo = {
            'class': cls,
            'fullname': cls.__module__ + '.' + cls.__name__,
            'instances': [],
        }
    
        self._classes.append(classinfo)


    def _get_class_info(self, cls):
        '''Returns the class info dictionary for the given class.'''
        
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
        

    def get_classes(self):
        '''Return a list of all classes'''
        
        return [clsinfo['class'] for clsinfo in self._classes]
