import mon.collectors.system
from mon.classreg import create_collector_instance
from time import sleep
from datetime import datetime
from mon.mqtt import MqttPublisher

config = {
    'global': {
        'prefix': 'mon',
        'broker': 'opi2',
        'port': 1883,
    },
    'collectors': [
        {
            'class': 'mon.collectors.system.LoadAvg',
            'interval': 4,
            
        },
    ]
}

def create_collectors(colcfg):
    collectors = []
    
    for cfg in colcfg:
        inst = create_collector_instance(
            clsname=cfg['class'],
            cfg=cfg)
        collectors.append(inst)

    return collectors


def main():
    collectors = create_collectors(config['collectors'])

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

