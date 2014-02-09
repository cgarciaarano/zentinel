#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
from logging.handlers import SysLogHandler 
import logging.config

import os
import sys
import redis
import hiredis

DEBUG = True

SYSLOG_FACILITY = 'local0'

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "persistent-messages"))

TIME_ZONE = 'Europe/Paris'

USE_TZ = True

#########################################################################################
###########                       REDIS CONFIG                              #############
#########################################################################################
APP_NAME = 'zentinel'

REDIS_IP = 'localhost'
REDIS_DB = 1

REDIS_EQUEUE_IP = REDIS_IP
REDIS_EQUEUE_DB = REDIS_DB
if REDIS_IP in ('localhost','127.0.0.1'):
	# REDIS_POOL = redis.ConnectionPool(max_connections=500, unix_socket_path='/var/run/redis/redis.sock')
	REDIS_POOL = redis.ConnectionPool(max_connections=500, host=REDIS_IP, db=REDIS_DB, port=6379)	# TODO Delete
else:
	REDIS_POOL = redis.ConnectionPool(max_connections=500, host=REDIS_IP, db=REDIS_DB, port=6379)

CONSUMED_EVENTS = 'CONSUMED_EVENTS'

#########################################################################################
###########                       RQ CONFIG                                 #############
#########################################################################################
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
#########################################################################################
###########                       ASTERISK CONFIG                           #############
#########################################################################################
ASTERISK_AMI_SERVERS = [ {	'host':'localhost',
							'port':8088,
							'user':'zentinel',
							'passwd':'tweetmary'} ]

#########################################################################################
###########                       LOGGING CONFIG                            #############
#########################################################################################
LOGGING = {
	'version': 1,
	'disable_existing_loggers': True,
	'formatters': {
		'verbose': {
			'format': '%(asctime)s APP:{0} PID:%(process)s %(filename)s %(funcName)s %(levelname)s %(message)s'.format(APP_NAME)
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