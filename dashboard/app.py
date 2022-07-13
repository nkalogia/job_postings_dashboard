import dash
import dash_bootstrap_components as dbc

from flask_caching import Cache

import os



app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
                suppress_callback_exceptions=True)

CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis:localhost:6379'),
    'CACHE_DEFAULT_TIMEOUT': 0
}

cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)


# server = app.server