import json
import logging

from flask import Flask, render_template, Response, abort
from jinja2.exceptions import TemplateNotFound

from .mqtt_listener import MqttListener
from .style import get_html_color, get_css_color

app = Flask(__name__)
app.jinja_env.globals.update(html_color=get_html_color, css_color=get_css_color)
port = 5000

cfg = {'broker': 'opi2', 'port': 1883, 'base_topic': 'mon'}
mqttl = MqttListener(cfg)


@app.route('/')
def host_list():
    hosts = mqttl.get_host_list()

    return render_template('hosts.html', hosts=hosts)


@app.route('/hostinfo/<host>')
def host_info(host):
    try:
        data = mqttl.get_host_data(host)
    except KeyError as e:
        return abort(404)

    rendered_items = []
    for key, item in data.items():

        try:
            tmpl = 'items/' + (item['_class'].split('.')[-1]) + '.html'
            itemhtml = render_template(tmpl, key=key, item=item)
            rendered_items.append(itemhtml)
            
        except TemplateNotFound as e:
            itemhtml = render_template('items/PreItem.html', key=key, item=item)
            rendered_items.append(itemhtml)
            
        except Exception as e:
            # other errors are currently just ignored
            print(item)
            logging.exception(e)
            continue
    
    return render_template('hostinfo.html', host=host, data=data, rendered_items=rendered_items)


@app.route('/rawhostinfo/<host>')
def raw_host_info(host):
    data = mqttl.get_host_data(host)

    return Response(json.dumps(data), mimetype='application/json')
