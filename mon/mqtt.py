import paho.mqtt.client as mqtt
import socket
import json


class MqttPublisher():
    def __init__(self, cfg):
        self._cfg = cfg

        self._prefix = cfg['prefix'] + '/' + socket.getfqdn() + '/'
        
        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        self.connect()
        
        # starts its own thread to handle network i/o
        self.client.loop_start()

        
    def connect(self):
        # set up the last will message (must be before connect)
        node_state_topic = self._prefix + 'node_state'
        
        self.client.will_set(
            topic=node_state_topic,
            payload=json.dumps('offline'),
            retain=True)
        
        self.client.connect(self._cfg['broker'], self._cfg['port'])

        
    def publish_data(self, data):
        for k in data:

            topic = self._prefix + k
            payload = json.dumps(data[k])
            
            self.client.publish(topic, payload, retain=True)
            
            print(topic, ':', payload)

            
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
        
