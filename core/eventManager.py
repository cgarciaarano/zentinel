#!/usr/bin/env python
# encoding: utf-8

"""
eventManager.py

Event Manager

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
import action,
import redis
from optparse import OptionParser
import time
import logging
import signal
import traceback
import ujson

sys.path.insert(0, '../')

import web.settings
setup_environ(web.settings)

web.settings.DEBUG = False
logger = logging.getLogger('web')

parser = OptionParser(description='Startup options')
# parser.add_option('--redis','-r',dest='redisIP',help='Redis server IP Address',metavar='REDIS',default='192.168.0.98')
parser.add_option('--redis','-r',dest='redisIP',help='Redis server IP Address',metavar='REDIS',default=web.settings.REDIS_IP)
parser.add_option('--redisdb','-d',dest='redisDB',help='Redis server DB',metavar='REDIS_DB',default=.settings.REDIS_DB)

(options, args) = parser.parse_args()

CONSUMED_EVENTS = 'CONSUMED_EVENTS'

class EventQueue():
	def __init__(self):
		self.rqueue = 'EVENT_QUEUE'
		self.redis_connect()

	def redis_connect():
		''' Reconnects to Redis and returns an active connection. Exits the program ir it can't '''
		attempts = 1
		got_redis = False
		
		while not got_redis and attempts < 10:
			try:
				logger.info("Trying Redis reconnection {0}...".format(attempts))
				rds = redis.Redis(options.redisIP,db=options.redisDB)
				rds.llen(self.rqueue)
				got_redis = True
				logger.info("Redis connected!")
			except Exception, e:
				logger.error("Could not connect to Redis at {0}: {1}. Trying again in 1 second".format(options.redisIP,e))
				time.sleep(1)
				attempts += 1

		if attempts == 10:
			logger.error("Reconnection to Redis {0} failed 10 times, exiting program".format(options.redisIP))
			sys.exit(-1)

		self.redis = rds


	def pop_event(self):
		try:
			event = self.redis.blpop(self.rqueue)[1]

			event = eval(event)
			total = self.redis.incr(CONSUMED_EVENTS,1) # Increment in redis the number of events consumed 
			logger.debug("Total events consumed {0}, processing...".format(total))
		except redis.ConnectionError:
			pass

		return event

	def push_event(self,event):
		try:
			rpipe = self.redis.pipeline()
			rpipe.rpush(self.rqueue,str(event))
			rpipe.decr(CONSUMED_EVENTS,1) # Decrement in redis the number of NCDRs consumed
			rpipe.execute()
			self.current_event = None
		except redis.ConnectionError:
			pass


class EventManager():
	def __init__(self):
		self.rqueue = EventQueue()
		self.current_event = None

	
	def consume_queue(self):
		''' Consumes an event and decides if it should be executed '''
		
		t0 = time.time()
		logger.info("Waiting for events to arrive...")
		self.current_event = rqueue.pop_event()

		try:
			action = self.current_event.getAction()

			logger.info("Event processed in {0} seconds".format(time.time()-t0))
			logger.debug("Action: {0}".format(action)

			if action:
				pass
				# Send to a worker to execute enqueue(action.execute())
			else:
				pass
				# Event discarded

		except Exception:
			logger.error("Failed processing event: {0} Data is {1}".format(traceback.format_exc(),event))
			logger.error("Sending data back to queue...")
			try:
				rqueue.push_event(self.current_event)
				logger.info("Data succesfully sent back to queue!")
			except:
				logger.crit("Could not send data back to queue")
				sys.exit(-1)
				
		self.current_event = None

	def run(self):
		while True:
			self.consume_queue()


def __signalHandler(signum, frame):

	logger.debug("Caught signal" + str(signum))

	try:
		logger.error("Signal recived while inserting, sending data back to queue...")

		try:
			event_manager.rqueue.push_event(event_manager.current_event)			
			logger.info("Data succesfully sent back to queue!")
		except:
			logger.debug("Something went wrong 1")

	except:
		logger.debug("Something went wrong 2 {0}".format(traceback.format_exc()))
	finally:
		raise KeyboardInterrupt



if __name__ == '__main__':
	event_manager = EventManager()
	signal.signal(signal.SIGTERM, __signalHandler)
	signal.signal(signal.SIGINT, __signalHandler)
	event_manager.run()