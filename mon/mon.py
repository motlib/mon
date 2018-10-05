from time import sleep
from datetime import datetime
from mon.mqtt import MqttPublisher

import ruamel.yaml

import mon.collectors
from mon.classreg import create_collector_instance, create_all_collectors


def load_config(filename):
    yaml = ruamel.yaml.YAML()
    with open(filename, 'r') as f:
        cfg = yaml.load(f)

    return cfg


def create_collectors(colcfg):
    collectors = []
    
    for cfg in colcfg:
        inst = create_collector_instance(
            clsname=cfg['class'],
            cfg=cfg)
        collectors.append(inst)

    return collectors


def main():
    config = load_config('./config/example.yaml')

    collectors = create_all_collectors()
    #collectors = create_collectors(config['collectors'])

    mqtt_pub = MqttPublisher(cfg=config['global'])
    
    while True:
        # find runnable collectors and run them
        runnables = (col for col in collectors if col.is_ready())
        for col in runnables:
            values = col.get_data()
            mqtt_pub.publish_data(values)

        # find next ready time of a collector
        next_run = min(col.get_next_run() for col in collectors)

        # we sleep additional 0.1 seconds to be sure the collector is ready 
        sleep_time = (next_run - datetime.now()).total_seconds() + .1

        print('sleeping', sleep_time)
        
        sleep(max(sleep_time, 0))

