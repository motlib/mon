import json
import logging
from datetime import datetime

from flask import Flask, render_template, Response, abort
from jinja2.exceptions import TemplateNotFound

from .mqtt_listener import MqttListener

from monsrv.factory import create_app

app = create_app()

cfg = {'broker': 'opi2', 'port': 1883, 'base_topic': 'mon'}
mqttl = MqttListener(cfg)


@app.route('/')
def host_list():
    hosts = mqttl.get_host_list()
    classes = mqttl.get_classes()

    return render_template('hostlist.html', hosts=hosts, classes=classes)


def render_item(host, item):
    try:
        age = (datetime.utcnow() - datetime.fromtimestamp(int(item['_timestamp']))).total_seconds()
        age = max(age, 0)
    except:
        age=0

    item['_age'] = age
    item['_next_update'] = int(item['_interval']) - age
    
    try:
        tmpl = 'items/{clsname}.html'.format(clsname=item['_class'])
        itemhtml = render_template(tmpl, host=host, item=item)
        return itemhtml
        
    except TemplateNotFound as e:
        itemhtml = render_template('items/PreItem.html', host=host, item=item)
        return itemhtml
        
    except Exception as e:
        # other errors are currently just ignored
        msg = "Failed to render item '{item}'."
        logging.exception(msg.format(
            item=item))

        return None
    

@app.route('/clsinfo/<clsname>')
def class_info(clsname):
    data = mqttl.get_class_data(clsname)

    print(data)
    
    rendered_items = []
    
    # sort by class name until we have a better idea
    for host in sorted(data.keys()):
        item = data[host]

        html = render_item(host, item)
        if html != None:
            rendered_items.append(html)

    return render_template(
        'clsinfo.html',
        clsname=clsname,
        data=data,
        rendered_items=rendered_items)
    
    

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

        html = render_item(host, item)
        if html != None:
            rendered_items.append(html)

    return render_template(
        'hostinfo.html',
        host=host,
        data=data,
        rendered_items=rendered_items)


@app.route('/rawhostinfo/<host>')
def raw_host_info(host):
    data = mqttl.get_host_data(host)

    return Response(json.dumps(data), mimetype='application/json')
