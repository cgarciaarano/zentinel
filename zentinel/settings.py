# -*- coding: utf-8 -*-
# encoding: utf-8
from logging.handlers import SysLogHandler 
import logging.config

import os
import redis
import hiredis

DEBUG = True

SYSLOG_FACILITY = 'local0'

PROJECT_ROOT = os.path.dirname(__file__)

TIME_ZONE = 'Europe/Paris'

USE_TZ = True

APP_NAME = 'zentinel'

#########################################################################################
###########                       WEB CONFIG                              #############
#########################################################################################
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

WEB_IPADDR = 'localhost'
WEB_PORT = 8080

DBDRIVER = 'postgresql'
DBUSER = 'postgres'
DBPASSWD = 'sp1d1clippeR!'
DBSERVER = 'localhost'
DBPORT = '5432'
DBNAME = 'zentinel'

SQLALCHEMY_DATABASE_URI = '{0}://{1}:{2}@{3}:{4}/{5}'.format(DBDRIVER,DBUSER,DBPASSWD,DBSERVER,DBPORT,DBNAME)
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_migrations')

SQLALCHEMY_BINDS = {
	'db_web' : SQLALCHEMY_DATABASE_URI,
	'db_data' : SQLALCHEMY_DATABASE_URI,
	}


CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]

#########################################################################################
###########                       CORE CONFIG                              #############
#########################################################################################
API_IPADDR = 'localhost'
API_PORT = 8000

###########                       ACTIONS CONFIG                              #############
MAX_CALL_DURATION = 60 # Maximum call duration, in seconds.


###########                       REDIS CONFIG                              #############
REDIS_IP = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 1
EXPIRATION = 60

REDIS_EQUEUE_IP = REDIS_IP
REDIS_EQUEUE_DB = REDIS_DB
REDIS_EQUEUE_PORT = REDIS_PORT
# REDIS_POOL = redis.ConnectionPool(max_connections=500, unix_socket_path='/var/run/redis/redis.sock')
REDIS_EVENT_POOL = redis.ConnectionPool(max_connections=500, host=REDIS_EQUEUE_IP, db=REDIS_EQUEUE_DB, port=REDIS_EQUEUE_PORT)

REDIS_WQUEUE_IP = REDIS_IP
REDIS_WQUEUE_DB = REDIS_DB
REDIS_WQUEUE_PORT = REDIS_PORT
REDIS_WORKER_POOL = redis.ConnectionPool(max_connections=500, host=REDIS_WQUEUE_IP, db=REDIS_WQUEUE_DB, port=REDIS_WQUEUE_PORT)

CONSUMED_EVENTS = 'CONSUMED_EVENTS'


###########                       CACHE CONFIG                              #############
CACHES = {
	'default': {
		'CACHE_TYPE': 'redis',
		'CACHE_KEY_PREFIX': APP_NAME,
		'CACHE_DEFAULT_TIMEOUT':2,
		'CACHE_REDIS_HOST':REDIS_IP,
		'CACHE_REDIS_PORT': REDIS_PORT,
		'CACHE_REDIS_DB':REDIS_DB,
		'OPTIONS': {
			'PARSER_CLASS':'redis.connection.HiredisParser',
		},
	},
}

###########                       RQ CONFIG                                 #############
RQ_TIMEOUT = 1800
"""
RQ_QUEUES = {
	'default': {
		'HOST': REDIS_IP,
		'PORT': 6379,
		'DB': REDIS_DB,
		'PASSWORD': '',
	},
}
"""

###########                       ASTERISK CONFIG                           #############
ASTERISK_AMI_SERVERS = [ {	'host':'localhost',
							'port':8088,
							'user':'zentinel',
							'passwd':'tweetmary'} ]


###########                       LOGGING CONFIG                            #############
LOGGING = {
	'version': 1,
	'disable_existing_loggers': True,
	'formatters': {
		'verbose': {
			'format': '%(asctime)s PID:%(process)s %(filename)s %(funcName)s %(levelname)s %(message)s'
		},
		'simple': {
			'format': '%(levelname)s %(message)s'
		},
	},
	'filters': {},
	'handlers': {
		'console':{
			'level':'DEBUG',
			'class':'logging.StreamHandler',
			'formatter': 'verbose'
		},
		 'rsyslog0': {
			'level': 'DEBUG',
			'class': 'logging.handlers.SysLogHandler',
			'formatter': 'verbose',
			'facility': 'local0',
			'address': '/dev/log',
			'filters': []
		},
		'rsyslog1': {
			'level': 'DEBUG',
			'class': 'logging.handlers.SysLogHandler',
			'formatter': 'verbose',
			'facility': 'local1',
			'address': '/dev/log',
			'filters': []
		},
	},
	'loggers': {
		"web": {
			"handlers": ['console',"rsyslog0"],
			"level": "DEBUG",
			"progagate": True,
		},
		"core": {
			"handlers": ['console',"rsyslog1"],
			"level": "DEBUG",
			"progagate": True,
		},
	}
}
logging.config.dictConfig(LOGGING)