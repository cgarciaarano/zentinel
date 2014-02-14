from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from momentjs import momentjs
sys.path.insert(0, '../')

web = Flask(__name__)
web.config.from_object('settings')
web.jinja_env.globals['momentjs'] = momentjs
db = SQLAlchemy(web)

from web import views, models
