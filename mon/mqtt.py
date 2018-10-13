from datetime import datetime
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

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        self._connect()
        
        # starts its own thread to handle network i/o
        self.client.loop_start()

        
    def _connect(self):
        # set up the last will message (must be set before connect) While
        # online, this data is generated ny the NodeInfo collector. Here it's
        # hardcoded for offline state.
        node_state_topic = self._prefix + 'NodeInfo'
        
        self.client.will_set(
            topic=node_state_topic,
            payload=json.dumps({'state': 'offline'}),
            retain=True)
        
        self.client.connect(self._cfg['broker'], self._cfg['port'])

        
    def _prepare_data(self, col):
        topic, data = col.get_data()
    
        data['_class'] = col.__module__ + '.' + col.__class__.__name__
        data['_timestamp'] = datetime.now().isoformat()
        data['_interval'] = col.get_interval()
        
        topic = self._prefix + topic

        return (topic, data)

    
    def publish_data(self, col):
        try:
            (topic, data) = self._prepare_data(col)
            
            payload = json.dumps(data)
            self.client.publish(topic, payload, retain=True)

            msg = 'MQTT public to {topic}: {payload}'
            logging.debug(msg.format(**locals()))
        except Exception as e:
            logging.exception("Failed to publish data from {0} collector.".format(col.__class__.__name__))
            

            
    def on_connect(self, mqttc, obj, flags, rc):
        # FIXME: should be using logging
        msg = 'MQTT client connected to broker (rc={rc})'        
        print(msg.format(rc=rc))

        # publish, that we are online now
        self.publish_data(data={'node_state': 'online'})


    def on_disconnect(self, mqttc, userdata, rc):
        # FIXME: should be using logging
        msg = 'MQTT client lost connection to broker (rc={rc})'        
        print(msg.format(rc=rc))
        
