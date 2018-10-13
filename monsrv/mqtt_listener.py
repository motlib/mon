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
        try:
            # strip base topic and following '/'
            subtopic = msg.topic[len(self._cfg['base_topic']) + 1:]

            (host, clsname) = subtopic.split('/', maxsplit=1)
        
            self._handle_message(host, clsname, msg.payload)
        except Exception as ex:
            # FIXME: this is in another thread with no logging enabled
            logging.exception("Failed to handle received message.")


    def _handle_message(self, host, clsname, sdata):
        #if rest == 'node_state':
        #    remove host
        with self._lock:
            data = json.loads(sdata)
            if clsname == 'NodeInfo' and data['state'] == 'offline':
                # we do not keep any data from offline hosts
                del self._hosts[host]
            else:
                if host not in self._hosts:
                    self._hosts[host] = {}

                self._hosts[host][clsname] = data
        

    def get_host_list(self):
        with self._lock:
            return list(self._hosts.keys())


    def get_host_data(self, host, key=None):
        with self._lock:
            return copy.deepcopy(self._hosts[host])
