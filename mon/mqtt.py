import paho.mqtt.client as mqtt
import socket

class MqttPublisher():
    def __init__(self, cfg):
        self._cfg = cfg

        self._prefix = cfg['prefix'] + '/' + socket.getfqdn() + '/'
        
        self.client = mqtt.Client()
        self.client.connect(cfg['broker'], cfg['port'])

        # starts its own thread to handle network i/o
        self.client.loop_start()

        
    def publish_data(self, data):
        for k in data:
            self.client.publish(self._prefix + k, data[k])
            
            print(k, '->', data[k])
