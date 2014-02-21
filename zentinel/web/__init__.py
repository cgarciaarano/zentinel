from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from momentjs import momentjs
import sys, os
from zentinel import settings

# Web stuff
web = Flask(__name__)
web.config.from_object('zentinel.settings')
web.jinja_env.globals['momentjs'] = momentjs

# DB stuff
db = SQLAlchemy(web)

# Login manager stuff
lm = LoginManager()
lm.init_app(web)
lm.login_view = 'login'
oid = OpenID(web, os.path.join(settings.basedir, 'tmp'))

from zentinel.web import views, models