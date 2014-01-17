#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
from logging.handlers import SysLogHandler 


import os
import sys
import redis

SYSLOG_FACILITY = 'local0'
INTERNAL_IPS = ('127.0.0.1','192.168.0.96')  # For django debug toolbar

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
REDIS_LT_PREFIX = 'LiveTraffic_{0}*'.format(APP_NAME)
REDIS_LT_PREFIX_USR = 'User_LiveTraffic_{0}*'.format(APP_NAME)
REDIS_PUB_SUB = 'LIVE_{0}*'.format(APP_NAME)
REDIS_PUB_SUB_USR = 'USER_LIVE_{0}*'.format(APP_NAME)
REDIS_ICX_USAGE = 'Icx_Usage_{0}*'.format(APP_NAME)
REDIS_CDR_PREFIX = 'CDRCONVERTER_{0}'.format(APP_NAME)

CHANNEL_GLOBAL_MESSAGES = 'international{0}'.format(APP_NAME)
CALLS_PROCESSED_JIZO = 'CALLS_PROCESSED_JIZO_{0}'.format(APP_NAME)
REQUESTS_PROCESSED_JIZO = 'REQUESTS_PROCESSED_JIZO_{0}'.format(APP_NAME)

#########################################################################################
###########                       REDIS CONFIG                              #############
#########################################################################################

EXECUTION_HASH_PREFIX = 'EXECUTION_HASH_{0}_'.format(APP_NAME)
EXECUTION_SKEY_PREFIX = 'EXECUTION_SKEY_{0}_'.format(APP_NAME)

REDIS_POOL = redis.ConnectionPool(max_connections=500, host=REDIS_IP, db=REDIS_DB, port=6379)
REDIS = redis.Redis(connection_pool=REDIS_POOL)
REDIS_PUB_SUB = REDIS.pubsub()
# REDIS_PUB_SUB.psubscribe(REDIS_PUB_SUB_USR)

REDIS_LT_PREFIX = 'LiveTraffic_{0}*'.format(APP_NAME)
REDIS_LT_PREFIX_USR = 'User_LiveTraffic_{0}*'.format(APP_NAME)
REDIS_PUB_SUB = 'LIVE_{0}*'.format(APP_NAME)
REDIS_PUB_SUB_USR = 'USER_LIVE_{0}*'.format(APP_NAME)
REDIS_ICX_USAGE = 'Icx_Usage_{0}*'.format(APP_NAME)
REDIS_CDR_PREFIX = 'CDRCONVERTER_{0}'.format(APP_NAME)
REDIS_ROUTETABLEUTILS_PREFIX = 'ROUTETABLEUTILS_{0}'.format(APP_NAME)
SCRIPT_STATUS_PREFIX = 'SCRIPTS_STATUS_{0}'.format(APP_NAME)
ROUTING_RESULT_PREFIX = 'ROUTING_RESULT_{0}|'.format(APP_NAME)

CHANNEL_GLOBAL_MESSAGES = 'international{0}'.format(APP_NAME)

CALLS_PROCESSED_JIZO = 'CALLS_PROCESSED_JIZO_{0}'.format(APP_NAME)
REQUESTS_PROCESSED_JIZO = 'REQUESTS_PROCESSED_JIZO_{0}'.format(APP_NAME)
ROUTETABLE_MAX_PROVIDERS = 15
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
		'null': {
			'level':'DEBUG',
			'class':'django.utils.log.NullHandler',
		},
		'console':{
			'level':'DEBUG',
			'class':'logging.StreamHandler',
			'formatter': 'verbose'
		},
		'mail_admins': {
			'level': 'ERROR',
			'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
			'filters': []
		},
	     'rsyslog1': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'verbose',
            'facility': SYSLOG_FACILITY,
            'address': '/dev/log',
            'filters': []
        },
	},
	'loggers': {
		"rq.worker": {
            "handlers": ['console',"rsyslog1"],
            "level": "DEBUG",
            "progagate": True,
        },
		"ooint.international.jobs": {
            "handlers": ['console',"rsyslog1"],
            "level": "DEBUG",
            "progagate": True,
        },        
		'django': {
			'handlers':['null'],
			'propagate': True,
			'level':'INFO',
		}
	}
}



RQ_QUEUES = {
    'default': {
        'HOST': REDIS_IP,
        'PORT': 6379,
        'DB': REDIS_DB,
        'PASSWORD': '',
    },
}