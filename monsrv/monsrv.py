import json
import logging

from flask import Flask, render_template, Response
from jinja2.exceptions import TemplateNotFound

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

    rendered_items = []
    for key, item in data.items():
        data = None
        try:
            tmpl = 'items/' + (item['_class'].split('.')[-1]) + '.html'
            data = render_template(tmpl, key=key, item=item)
        except TemplateNotFound as e:
            data = render_template('items/PreItem.html', key=key, item=item)
        except Exception as e:
            # other errors are currently just ignored
            logging.exception(e)
            continue

        rendered_items.append(data)
    
    return render_template('hostinfo.html', host=host, data=data, rendered_items=rendered_items)


@app.route('/rawhostinfo/<host>')
def raw_host_info(host):
    data = mqttl.get_host_data(host)

    return Response(json.dumps(data), mimetype='application/json')


if __name__ == '__main__':
    cfg = {'broker': 'opi2', 'port': 1883, 'base_topic': 'mon'}
    mqttl = MqttListener(cfg)

    app.run(host='0.0.0.0', port=port, debug=True)
    
