import json
import logging
import socket

import paho.mqtt.client as mqtt


class MqttPublisher():
    def __init__(self, cfg, verbose=False):
        self._cfg = cfg
        self._verbose = verbose

        # we use the configured prefix plus our FQDN as the root topic. 
        self._prefix = cfg['prefix'] + '/' + socket.getfqdn() + '/'
        
        self.client = mqtt.Client()

        self.client.enable_logger(logging.getLogger())
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        
    def connect(self):
        self.client.connect(self._cfg['broker'], self._cfg['port'])

        # starts its own thread to handle network i/o
        self.client.loop_start()
        logging.info('Spawned mqtt publisher thread.')


    def set_last_will(self, topic, payload):
        self.client.will_set(
            topic=self._prefix + topic,
            payload=json.dumps(payload),
            retain=True)
        
        
    def _prepare_data(self, col):
        topic, data = col.get_data()
            
        topic = self._prefix + topic

        return (topic, data)

    
    def publish_data(self, topic, payload):
        self.client.publish(
            self._prefix + topic,
            payload,
            retain=True)

        msg = 'MQTT public to {topic}: {payload}'
        logging.debug(msg.format(**locals()))

        # no logging of exceptions here. This is done in the scheduler.
        
            
    def on_connect(self, mqttc, obj, flags, rc):
        '''Event handler for MQTT connect event.'''
        
        msg = 'MQTT client connected to broker (rc={rc})'        
        logging.info(msg.format(rc=rc))


    def on_disconnect(self, mqttc, userdata, rc):
        '''Event handler for MQTT disconnect event.'''
        
        msg = 'MQTT client lost connection to broker (rc={rc})'        
        logging.info(msg.format(rc=rc))
        
