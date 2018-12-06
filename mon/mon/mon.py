import argparse
import json
import logging
import os

import ruamel.yaml

from mon.classreg import ClassRegistry
from mon.collectors.node import NodeInfo
from mon.mqtt import MqttPublisher
from mon.scheduler import Scheduler
import mon.__version__


def load_config(filename):
    '''Load the YAML configuration file specified by filename.'''
    
    yaml = ruamel.yaml.YAML()
    with open(filename, 'r') as f:
        cfg = yaml.load(f)

    return cfg


def parse_cmdline(args=None):
    '''Parse command-line options.

    :param args: If None, parse sys.argv. Otherwise parse args as a list of 
      command-line options.'''
    
    parser = argparse.ArgumentParser(
        prog=mon.__version__.__title__,
        description='')

    parser.add_argument(
        '-c', '--config',
        help='Directory containing configuration files.',
        required=False,
        default=None)

    parser.add_argument(
        '-v', '--verbose',
        help='Verbose output',
        action='store_true')

    return parser.parse_args(args)


def setup_logging(verbose=False):
    '''Set up logging. 

    :param verbose: If set to true, enable verbose logging output (i.e. print 
      log message with DEBUG level. Otherwise only up to INFO level).'''
    
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=level)
    

def create_collectors(cfg):
    '''Find all collector classes and instanciate them. 

    :returns: Class registry.'''
    
    # we import collectors here, so logging is already initialized.
    import mon.collectors
    from mon.collectors.base import CollectorBase
    
    registry = ClassRegistry()

    registry.find_classes(
        module=mon.collectors,
        baseclass=CollectorBase)

    classes = registry.get_classes()
    msg = 'Registered {0} collectors: {1}'
    
    names = sorted([cls.__name__ for cls in classes])
    logging.info(msg.format(len(classes), ', '.join(names)))

    registry.create_all_instances(cfg)

    return registry



class MqttCollectorPublisher():
    def __init__(self, mqtt):
        self._mqtt = mqtt

    def publish(self, col):
        (topic, data) = col.get_data()
        payload = json.dumps(data)

        
        self._mqtt.publish_data(topic, payload)

    
def main():
    args = parse_cmdline()
    setup_logging(args.verbose)

    
    if args.config != None:
        cfg_dir = args.config
    else:
        cfg_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
        'config'))


    collector_cfg = load_config(
        filename=os.path.join(cfg_dir, 'collectors.yaml'))

    mqtt_cfg = load_config(
        filename=os.path.join(cfg_dir, 'mqtt.yaml'))

    # find all collectors and create instances
    registry = create_collectors(collector_cfg)
        
    
    mqtt_pub = MqttPublisher(
        cfg=mqtt_cfg,
        verbose=args.verbose
    )

    # Prepare the offline data and set if as last will
    
    node_info = registry.get_instance_by_class(NodeInfo)

    node_info.set_state('offline')
    (topic, payload) = node_info.get_data()
    
    mqtt_pub.set_last_will(topic, payload)
    # set back state to online for normal publishing 
    node_info.set_state('online')

    mqtt_col_pub = MqttCollectorPublisher(mqtt_pub)
    
    scheduler = Scheduler(work_fct=mqtt_col_pub.publish)
#        work_fct=lambda col: mqtt_pub.publish_data(col))

    for c in registry.get_all_instances():
        scheduler.add_task(c, c.get_interval())

    # run the scheduler until end of time
    try:
        logging.info('Kicking off the scheduler.')
        scheduler.run()
    except KeyboardInterrupt:
        logging.info('Shutting down due to user request. Bye!')
