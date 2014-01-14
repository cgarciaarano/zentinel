from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from momentjs import momentjs

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = momentjs
db = SQLAlchemy(app)

from app import views, models