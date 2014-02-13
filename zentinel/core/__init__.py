from flask import Flask
from flask.ext.cache import Cache

api_server = Flask(__name__)
#cache = Cache(api_server)

import api