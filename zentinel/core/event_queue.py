#!/usr/bin/env python
# encoding: utf-8

"""
event_queue.py

Event Queue

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
import zen_event, core_utils
from zentinel import settings

import logging
import sys
import time
import redis 
import datetime
import traceback	

logger = logging.getLogger('core')


class EventQueue():
	"""
	Queue of events. It uses Redis as backend, and permits duplicated events.
	Pop is blocked until a new event is pushed.
	"""
	def __init__(self):
		logger.debug("Creating EventQueue...")
		self.queue = 'EVENT_QUEUE'
		self.redis = core_utils.redis_connect(settings.REDIS_EVENT_POOL)

	def reset_counter(self):
		self.redis.set(settings.CONSUMED_EVENTS,0)

	def pop_event(self):
		try:
			event = self.redis.blpop(self.queue)[1]

			event = eval(event)

			total = self.redis.incr(settings.CONSUMED_EVENTS,1) # Increment in redis the number of events consumed 
			logger.info("Total events consumed {0}, processing...".format(total))

			event_object = zen_event.Event.from_dict(event)
			return event_object
		except redis.ConnectionError:
			logger.error('Connection error in Redis popping event')
		except Exception:
			logger.error('Unexpected exception. Trying to put data back in queue.')
			logger.error(traceback.format_exc())
			try: 
				self.redis.rpush(self.queue,event)
				logger.debug('Data pushed back in queue successfully')
			except Exception:
				logger.critical("Can't put data back in Redis. Logging data: {0}".format(event))

	def push_event(self, event):
		try:
			self.redis.rpush(self.queue,event.get_data())
			logger.debug('Event pushed in queue successfully')
		except redis.ConnectionError:
			logger.error('Connection error in Redis pushing event')