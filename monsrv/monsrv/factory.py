from flask import Flask

from monsrv.utils.style import get_html_color, get_css_color
from monsrv.utils.format import fmt_bytes, fmt_sig, fmt_date_interval


def create_app():
    app = Flask('monsrv')
    
    app.jinja_env.globals.update(
        html_color=get_html_color,
        css_color=get_css_color,
        fmt_bytes=fmt_bytes,
        fmt_sig=fmt_sig,
        fmt_date_interval=fmt_date_interval)

    return app
