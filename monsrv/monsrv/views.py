from datetime import datetime
import json
import logging

from flask import render_template, Response, abort
from jinja2.exceptions import TemplateNotFound

from monsrv import app
from monsrv import mqtt_db


@app.route('/')
def index():
    hosts = mqtt_db.get_hosts()
    classes = mqtt_db.get_classes()

    return render_template(
        'index.html',
        hosts=hosts,
        classes=classes)


def _update_item_age(item):
    '''Sets the _age and _next_update values for in the item data.'''
    
    try:
        age = int(datetime.utcnow().timestamp()) - item['_timestamp']
        
        # depending on the time offset of the sender, the age might get negative.
        age = max(age, 0)
    except Exception as ex:
        age = 0
        logging.exception('Failed to calculate item age.')

    item['_age'] = age
    item['_next_update'] = int(item['_interval']) - age


def _update_all_items_age(items):
    '''Update item age and next_update values and returns the minimum value for 
    _next_update.'''
    
    for item in items:
        _update_item_age(item)

    min_update = min(item['_next_update'] for item in items)

    # we add two seconds minimum for refreshing the web page
    min_update = max(min_update, 5)
    
    return min_update


def _render_item(host, item):
    '''Render an item template. 

    This function tries to locate the correct template by class name. If the
    template cannot be found, a default template is rendered.

    If an exception is raised during template rendering, the error is logged and
    None returned. Otherwise the rendered html code is returned.

    '''
    
    try:
        tmpl = 'items/{clsname}.html'.format(clsname=item['_class'])
        
        itemhtml = render_template(
            tmpl,
            host=host,
            item=item)
        
        return itemhtml
        
    except TemplateNotFound as e:
        itemhtml = render_template(
            'items/item_raw.html',
            host=host,
            item=item)
        
        return itemhtml
        
    except Exception as e:
        # other errors are only logged
        msg = "Failed to render item '{item}'."
        logging.exception(msg.format(
            item=item))

        return render_template(
            'items/item_error.html',
            item=item,
            clsname=item['_class'],
            host=host,
            error_msg=e)
            
    

@app.route('/clsinfo/<clsname>')
def class_info(clsname):
    '''Show info by class name.'''
    
    items = mqtt_db.get_class_data(clsname)

    min_update_time = _update_all_items_age(items.values())
    
    rendered_items = []
    
    # sort by class name until we have a better idea
    for host in sorted(items.keys()):
        item = items[host]

        html = _render_item(host, item)
        if html != None:
            rendered_items.append(html)

    return render_template(
        'clsinfo.html',
        clsname=clsname,
        rendered_items=rendered_items,
        min_update=min_update_time)
    
    
@app.route('/hostinfo/<host>')
def host_info(host):
    try:
        items = mqtt_db.get_host_data(host)
    except KeyError as e:
        return abort(404)

    min_update_time = _update_all_items_age(items.values())
        
    rendered_items = []
    
    # sort by class name until we have a better idea
    for key in sorted(items.keys()):
        item = items[key]

        html = _render_item(host, item)
        if html != None:
            rendered_items.append(html)

    return render_template(
        'hostinfo.html',
        host=host,
        rendered_items=rendered_items,
        min_update_time=min_update_time)


@app.route('/rawhostinfo/<host>')
def raw_host_info(host):
    try:
        data = mqtt_db.get_host_data(host)

        return Response(
            json.dumps(data, indent=2),
            mimetype='application/json')
    
    except KeyError:
        return abort(404)
        
@app.route('/item/<host>/<clsname>')
def item(host, clsname):
    try:
        item = mqtt_db.get_host_item_data(host, clsname)
    
        return _render_item(host, item)
    except KeyError:
        return abort(404)
   
