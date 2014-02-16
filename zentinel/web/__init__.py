from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from momentjs import momentjs
import sys
sys.path.insert(0, '../')

web = Flask(__name__)
web.config.from_object('zentinel.settings')
web.jinja_env.globals['momentjs'] = momentjs
db = SQLAlchemy(web)

from zentinel.web import views, models