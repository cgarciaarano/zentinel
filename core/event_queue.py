#!/usr/bin/env python
# encoding: utf-8

"""
event_queue.py

Event Queue

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
from event import Event
import logging
import sys
import time

logger = logging.getLogger('kk')
sys.path.insert(0, '../')

import web.settings
class EventQueue():
	"""
	Queue of events. It uses Redis as backend, and permits duplicated events.
	Pop is blocked until a new event is pushed.
	"""
	def __init__(self):
		self.queue = 'EVENT_QUEUE'
		self.redis = self.redis_connect()

	def redis_connect(self):
		''' Reconnects to Redis and returns an active connection. Exits the program if it can't '''
		attempts = 1
		got_redis = False
		
		while not got_redis and attempts < 10:
			try:
				logger.info("Trying Redis reconnection {0}...".format(attempts))
				rds = redis.Redis(web.settings.REDIS_IP,db=web.settings.REDIS_DB)
				rds.llen(self.queue)
				got_redis = True
				logger.info("Redis connected!")
			except Exception, e:
				logger.error("Could not connect to Redis at {0}: {1}. Trying again in 1 second".format(web.settings.REDIS_IP,e))
				time.sleep(1)
				attempts += 1

		if attempts == 10:
			logger.error("Reconnection to Redis {0} failed 10 times, exiting program".format(web.settings.REDIS_IP))
			sys.exit(-1)

		return rds


	def pop_event(self):
		try:
			event = self.redis.blpop(self.queue)[1]

			event = eval(event)
			total = self.backend.incr(CONSUMED_EVENTS,1) # Increment in redis the number of events consumed 
			logger.debug("Total events consumed {0}, processing...".format(total))
		except redis.ConnectionError:
			pass

		return Event(event)

	def push_event(self, event):
		try:
			rpipe = self.redis.pipeline()
			rpipe.rpush(self.queue,str(event))
			rpipe.decr(CONSUMED_EVENTS,1) # Decrement in redis the number of NCDRs consumed
			rpipe.execute()
			self.current_event = None
		except redis.ConnectionError:
			pass