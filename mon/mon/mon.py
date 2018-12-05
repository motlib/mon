import argparse
import logging
import os

import ruamel.yaml

#from mon.classreg import create_collectors, find_collectors
from mon.classreg import ClassRegistry
from mon.mqtt import MqttPublisher
from mon.scheduler import Scheduler
import mon.__version__


def load_config(filename):
    yaml = ruamel.yaml.YAML()
    with open(filename, 'r') as f:
        cfg = yaml.load(f)

    return cfg


def parse_cmdline(args=None):
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
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=level)
    

def main():
    args = parse_cmdline()
    setup_logging(args.verbose)

    # we import collectors here, so logging is already initialized.
    import mon.collectors
    from mon.collectors.base import CollectorBase
    
    registry = ClassRegistry()

    registry.find_classes(
        module=mon.collectors,
        baseclass=CollectorBase)
    
    #find_collectors(mon.collectors)

    
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

    registry.create_all_instances(collector_cfg)

    collectors = registry.get_all_instances()

    mqtt_cfg = load_config(
        filename=os.path.join(cfg_dir, 'mqtt.yaml'))

    mqtt_pub = MqttPublisher(
        cfg=mqtt_cfg,
        verbose=args.verbose
    )

    scheduler = Scheduler(
        work_fct=lambda col: mqtt_pub.publish_data(col))

    for c in collectors:
        scheduler.add_task(c, c.get_interval())

    # run the scheduler until end of time
    try:
        logging.info('Kicking off the scheduler.')
        scheduler.run()
    except KeyboardInterrupt:
        logging.info('Shutting down due to user request. Bye!')
