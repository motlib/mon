import logging
from datetime import datetime


from monsrv.factory import create_app
from monsrv.mqtt_listener import MqttListener


app = create_app()

cfg = {'broker': 'opi2', 'port': 1883, 'base_topic': 'mon'}
mqttl = MqttListener(cfg)


import monsrv.views

