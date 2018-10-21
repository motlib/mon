'''Component to listen to MQTT messages and put them to its in-memory
database.'''

import copy
import json
import logging
import threading

import paho.mqtt.client as mqtt


class MqttListener():
    def __init__(self, cfg):
        self._cfg = cfg
        
        self.client = mqtt.Client()

        self.client.enable_logger(logging.getLogger())

        if 'user' in cfg and 'password' in cfg:
            client.username_pw_set(
                self._cfg['user'],
                self._cfg['password'])

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.client.connect(cfg['broker'], cfg['port'])
        self.client.loop_start()

        # the database is a simple dict
        self._hosts = {}

        self._lock = threading.Lock()

        
    def on_connect(self, client, userdata, flags, rc):
        '''On connect MQTT event handler'''
        
        topic = self._cfg['base_topic'] + '/#'
        client.subscribe(topic)


    def on_message(self, client, userdata, msg):
        '''On message MQTT event handler.'''
        try:
            # strip base topic and following '/'
            subtopic = msg.topic[len(self._cfg['base_topic']) + 1:]

            (host, clsname) = subtopic.split('/', maxsplit=1)
        
            self._handle_message(host, clsname, msg.payload)
        except Exception as ex:
            # FIXME: this is in another thread with no logging enabled
            logging.exception("Failed to handle received message.")


    def _handle_message(self, host, clsname, sdata):
        '''Put message to local in-memory database. Remove data if host goes
        offline.'''

        data = json.loads(sdata)

        #t = data['_timestamp']
        
        with self._lock:
            if clsname == 'NodeInfo':
                if data['state'] == 'offline':
                # we do not keep any data from offline hosts
                    del self._hosts[host]
                else:
                    # We do not add the nodeinfo data, so just pass.
                    pass
            else:
                if host not in self._hosts:
                    self._hosts[host] = {}

                self._hosts[host][clsname] = data
        

    def get_host_list(self):
        '''Returns a list of all known hosts.'''
        
        with self._lock:
            return list(sorted(self._hosts.keys()))


    def get_host_data(self, host):
        '''Returns all known data of a host.'''
        
        with self._lock:
            return copy.deepcopy(self._hosts[host])


    def get_class_data(self, clsname):
        '''Return a dict of host -> data items where data items are of type classname.'''
        
        with self._lock:

            data = {}

            # FIXME: Currently a host can only have one item per class
            #for host, hdata in self._hosts.items():
            #    for v in hdata.values():
            #        if v['_class'] == clsname:
            #            data[host] = v
            
            data = {
                host: v
                for host, hdata in self._hosts.items()
                for v in hdata.values()
                if v['_class'] == clsname
            }
            
            return data

    def get_classes(self):
        with self._lock:
            classes = {
                v['_class']
                for hdata in self._hosts.values()
                for v in hdata.values()
            }

            return classes
        
