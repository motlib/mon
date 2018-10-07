from flask import Flask, render_template
from mqtt_listener import MqttListener

app = Flask(__name__)

port = 5000

mqttl = None


@app.route('/')
def host_list():
    hosts = mqttl.get_host_list()

    return render_template('hosts.html', hosts=hosts)

@app.route('/hostinfo/<host>')
def host_info(host):
    data = mqttl.get_host_data(host)

    return render_template('hostinfo.html', host=host, data=data)



if __name__ == '__main__':
    cfg = {'broker': 'opi2', 'port': 1883, 'base_topic': 'mon'}
    mqttl = MqttListener(cfg)

    app.run(host='0.0.0.0', port=port, debug=True)
    
