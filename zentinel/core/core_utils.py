#!/usr/bin/env python
# encoding: utf-8

"""
core_utils.py

Utils

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
from zentinel import settings
import zen_event

import logging
import sys
import time
import redis 
import datetime
import traceback
from rq import Queue
from redis import StrictRedis

logger = logging.getLogger('core')

def redis_connect(pool):
	''' Reconnects to Redis and returns an active connection. Exits the program if it can't '''
	attempts = 1
	got_redis = False
	
	while not got_redis and attempts < 10:
		try:
			logger.info("Trying Redis {1} connection {0}...".format(attempts,pool))
			rds = redis.StrictRedis(connection_pool=pool)
			if rds.ping() is not None:
				got_redis = True
			logger.info("Redis connected!")
		except Exception, e:
			logger.error("Could not connect to Redis at {0}: {1}. Trying again in 1 second".format(pool,e))
			time.sleep(1)
			attempts += 1

	if attempts == 10:
		logger.error("Reconnection to Redis {0} failed 10 times, exiting program".format(pool))
		sys.exit(-1)

	return rds

class WorkerQueue(Queue):
	def __init__(self):
		logger.debug("Creating WorkerQueue...")
		redis_conn = redis_connect(settings.REDIS_WORKER_POOL)
		# Creates sync queue if Debug=True
		Queue.__init__(self, connection=redis_conn,async=not(settings.DEBUG))

class SharedMem():
	"""
	Shared memory implemented by Redis
	"""
	def __init__(self): 
		logger.debug("Creating SharedMem...")
		self.redis = redis_connect(settings.REDIS_WORKER_POOL)
		self.expiration = settings.EXPIRATION

	def get(self, key):
		""" Gets value and reset the expiration """
		try:
			data = self.redis.get(key)
			
			if data is not None:
				self.redis.expire(key, self.expiration)
			
			return data

		except redis.ConnectionError:
			logger.error('Connection error in Redis getting value for {0}'.format(key))
			logger.error(traceback.format_exc())
		except Exception:
			logger.error('Unexpected exception getting value for {0}'.format(key))
			logger.error(traceback.format_exc())

	def set(self, key, data):
		""" Sets value and expiration """
		try:
			if self.redis.setex(key, self.expiration, data) == 'OK':
				return True
			else:
				return False
			
		except redis.ConnectionError:
			logger.error('Connection error in Redis trying to set value {0} for key {1}'.format(data,key))
			logger.error(traceback.format_exc())
		except Exception:
			logger.error('Unexpected exception trying to set value {0} for key {1}'.format(data,key))
			logger.error(traceback.format_exc())
	
	def exists(self, key):
		""" Checks the presence of a key, and resets it's expiration if exists """
		if self.get(key) is None:
			return False
		else:
			return True