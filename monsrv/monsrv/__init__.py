from argparse import ArgumentParser
import logging
from datetime import datetime
import sys

from flask import Flask
import ruamel.yaml

from monsrv.mqtt import MqttListener, MqttDb


def parse_args():
    '''Set up command-line parser and parse arguments.'''
    parser = ArgumentParser()

    parser.add_argument(
        '-c', '--config',
        help='Configuration file',
        required=True)

    parser.add_argument(
        '-d', '--debug',
        help='Enabled web application debugging mode',
        action='store_true',
        default=False)

    parser.add_argument(
        '-i', '--interface',
        help='Interface to listen on (default 127.0.0.1)',
        default='127.0.0.1')

    parser.add_argument(
        '-p', '--port',
        help='Port to listen on (default 5000)',
        default='5000')
               
    return parser.parse_args()


def load_config(filename):
    yaml = ruamel.yaml.YAML()
    with open(filename, 'r') as f:
        cfg = yaml.load(f)

    return cfg


args = parse_args()

cfg = load_config(args.config)

app = Flask('monsrv')


mqtt_db = MqttDb(cfg)
mqtt_listener = MqttListener(cfg)
mqtt_listener.set_msg_handler(mqtt_db.handle_mqtt_message)


import monsrv.fmt
import monsrv.views

