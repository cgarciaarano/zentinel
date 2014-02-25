from zentinel.core.api.api import API
from flask import Flask

# API stuff
api_server = Flask(__name__)
api_manager = API()

from zentinel.core.api import views