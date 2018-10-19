import json
import logging
from datetime import datetime

from flask import Flask, render_template, Response, abort
from jinja2.exceptions import TemplateNotFound

from .mqtt_listener import MqttListener
from .style import get_html_color, get_css_color
from .format import fmt_bytes, fmt_sig, fmt_date_interval

app = Flask(__name__)
app.jinja_env.globals.update(
    html_color=get_html_color,
    css_color=get_css_color,
    fmt_bytes=fmt_bytes,
    fmt_sig=fmt_sig,
    fmt_date_interval=fmt_date_interval)


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
    
    # sort by class name until we have a better idea
    for key in sorted(data.keys()):
        item = data[key]

        try:
            age = (datetime.utcnow() - datetime.fromtimestamp(int(item['_timestamp']))).total_seconds()
            age = max(age, 0)
        except:
            age=0

        item['_age'] = age
        item['_next_update'] = int(item['_interval']) - age
        try:
            tmpl = 'items/' + (item['_class'].split('.')[-1]) + '.html'
            itemhtml = render_template(tmpl, key=key, item=item)
            rendered_items.append(itemhtml)
            
        except TemplateNotFound as e:
            itemhtml = render_template('items/PreItem.html', key=key, item=item)
            rendered_items.append(itemhtml)
            
        except Exception as e:
            # other errors are currently just ignored
            logging.exception("Failed to render item '{item}'.".format(item))
            continue
    
    return render_template('hostinfo.html', host=host, data=data, rendered_items=rendered_items)


@app.route('/rawhostinfo/<host>')
def raw_host_info(host):
    data = mqttl.get_host_data(host)

    return Response(json.dumps(data), mimetype='application/json')
