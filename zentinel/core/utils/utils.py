"""
utils.py

Common utilities in core package

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
from zentinel import settings
from zentinel.core import logger
from zentinel.web.models import Event

import logging
import sys
import time
import datetime
import redis 
import traceback
from rq import Queue
from redis import StrictRedis

def redis_connect(pool):
	''' Reconnects to Redis and returns an active connection. Exits the program if it can't '''
	attempts = 1
	got_redis = False
	
	while not got_redis and attempts < 3:
		try:
			logger.debug("Trying Redis {1} connection {0}...".format(attempts,pool))
			rds = redis.StrictRedis(connection_pool = pool, socket_timeout=0.1)
			if rds.ping() is not None:
				got_redis = True
			logger.info("Redis connected!")
		except Exception, e:
			logger.error("Could not connect to Redis at {0}: {1}. Trying again in 1 second".format(pool,e))
			attempts += 1

	if attempts == 3:
		logger.error("Reconnection to Redis {0} failed 3 times, exiting program".format(pool))
		sys.exit(-1)

	return rds

class WorkerQueue(Queue):
	"""
	Queue used to communicate with workers
	"""
	def __init__(self):
		logger.info("Creating WorkerQueue...")
		redis_conn = redis_connect(settings.REDIS_WORKER_POOL)
		# Creates sync queue if Debug=True
		Queue.__init__(self, connection=redis_conn,async=not(settings.DEBUG))

class SharedMem(object):
	"""
	Shared memory implemented by Redis
	"""
	def __init__(self): 
		logger.info("Creating SharedMem...")
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

class EventQueue(object):
	"""
	Queue of events. It uses Redis as backend, and permits duplicated events.
	Pop is blocked until a new event is pushed.
	"""
	def __init__(self):
		logger.info("Creating EventQueue...")
		self.queue = 'EVENT_QUEUE'
		self.redis = redis_connect(settings.REDIS_EVENT_POOL)

	def reset_counter(self):
		self.redis.set(settings.CONSUMED_EVENTS,0)

	def pop_event(self):
		try:
			event = self.redis.blpop(self.queue)[1]

			event = eval(event)

			total = self.redis.incr(settings.CONSUMED_EVENTS,1) # Increment in redis the number of events consumed 
			logger.info("Total events consumed {0}, processing...".format(total))

			event_object = Event.from_dict(event)
			return event_object
		except redis.ConnectionError:
			logger.error('Connection error in Redis popping event.')
			logger.error(traceback.format_exc())
		except Exception:
			logger.error('Unexpected exception. Trying to put data back in queue.')
			logger.error(traceback.format_exc())
			try: 
				self.redis.rpush(self.queue,event.get_data())
				logger.debug('Data pushed back in queue successfully')
			except Exception:
				logger.critical("Can't put data back in Redis. Logging data: {0}".format(event))

	def push_event(self, event):
		try:
			self.redis.rpush(self.queue,event.get_data())
			logger.debug('Event pushed in queue successfully {0}'.format(event.get_data()))
		except redis.ConnectionError:
			logger.error('Connection error in Redis pushing event')