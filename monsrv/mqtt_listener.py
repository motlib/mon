import copy
import json
import threading

import paho.mqtt.client as mqtt


class MqttListener():
    def __init__(self, cfg):
        self._cfg = cfg
        
        self.client = mqtt.Client()
        #client.username_pw_set(username, password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.client.connect(cfg['broker'], cfg['port'])
        self.client.loop_start()

        self._hosts = {}

        self._lock = threading.Lock()

        
    def on_connect(self, client, userdata, flags, rc):
        topic = self._cfg['base_topic'] + '/#'
        client.subscribe(topic)


    def on_message(self, client, userdata, msg):

        # strip base topic and following '/'
        subtopic = msg.topic[len(self._cfg['base_topic']) + 1:]

        (host, rest) = subtopic.split('/', maxsplit=1)

        #if rest == 'node_state':
        #    remove host
        with self._lock:
            if host not in self._hosts:
                self._hosts[host] = {}

            self._hosts[host][rest] = json.loads(msg.payload)

        
    def get_host_list(self):
        with self._lock:
            return list(self._hosts.keys())


    def get_host_data(self, host, key=None):
        with self._lock:
            return copy.deepcopy(self._hosts[host])
