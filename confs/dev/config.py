import os
import pytz
basedir = os.path.abspath(os.path.dirname(__file__))

IPADDR = '172.16.6.9'
PORT = 8001

DBDRIVER = 'mysql'
DBUSER = 'sms'
DBPASSWD = 'flask'
DBSERVER = 'localhost'
DBPORT = '3306'
DBNAME = 'sms_subscriber'

SQLALCHEMY_DATABASE_URI = '{0}://{1}:{2}@{3}:{4}/{5}'.format(DBDRIVER,DBUSER,DBPASSWD,DBSERVER,DBPORT,DBNAME)
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_migrations')

SQLALCHEMY_BINDS = {
	'db1' : SQLALCHEMY_DATABASE_URI,
	'kannel' : '{0}://{1}:{2}@{3}:{4}/{5}'.format(DBDRIVER,DBUSER,DBPASSWD,DBSERVER,DBPORT,'kannel')
	}


CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'