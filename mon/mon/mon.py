import argparse
import logging
import os

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
        help='Directory containing configuration files.',
        required=False,
        default=None)

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

    # we import collectors here, so logging is already initialized.
    import mon.collectors


    if args.config != None:
        cfg_dir = args.config
    else:
        cfg_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
        'config'))


    if args.all_collectors:
        # for testing, create an instance of all collectors with default config
        msg = 'Creating instances of all collectors, overriding configuration.'
        logging.info(msg)

    collector_cfg = load_config(os.path.join(cfg_dir, 'collectors.yaml'))

    collectors = create_collectors(
        collector_cfg,
        create_all=args.all_collectors)

    mqtt_cfg = load_config(os.path.join(cfg_dir, 'mqtt.yaml'))

    mqtt_pub = MqttPublisher(
        cfg=mqtt_cfg,
        verbose=args.verbose
    )

    scheduler = Scheduler(
        work_fct=lambda col: mqtt_pub.publish_data(col))

    for c in collectors:
        scheduler.add_task(c, c.get_interval())

    # run the scheduler until end of time
    logging.debug('Kicking off the scheduler.')
    scheduler.run()
