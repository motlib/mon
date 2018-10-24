import logging
from datetime import datetime

from flask import Flask

from monsrv.mqtt import MqttListener, MqttDb

app = Flask('monsrv')

cfg = {'broker': 'opi2', 'port': 1883, 'base_topic': 'mon'}

mqtt_db = MqttDb(cfg)
mqtt_listener = MqttListener(cfg)
mqtt_listener.set_msg_handler(mqtt_db.handle_mqtt_message)


import monsrv.fmt
import monsrv.views

