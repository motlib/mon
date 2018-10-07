import argparse
import logging

import ruamel.yaml

from mon.classreg import create_collectors
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
        help='Configuration file name',
        required=True)

    parser.add_argument(
        '-a', '--all-collectors',
        help=(
            'Create instances of all collectors instead of the ones listed in '
            'the configuration. '),
        action='store_true')

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

    # we do this here in the function, so logging is already available during
    # import of the collectors.
    import mon.collectors

    config = load_config(args.config)

    if args.all_collectors:
        # for testing, create an instance of all collectors with default config
        msg = 'Creating instances of all collectors, overriding configuration.'
        logging.info(msg)

    collectors = create_collectors(
        config['collectors'],
        create_all=args.all_collectors)

    mqtt_pub = MqttPublisher(
        cfg=config['global']
    )

    def pub_collector_values(col):
        mqtt_pub.publish_data(col)

    scheduler = Scheduler(
        tasks=collectors,
        work_fct=pub_collector_values)

    # run the scheduler until end of time
    logging.debug('Kicking off the scheduler.')
    scheduler.run()
