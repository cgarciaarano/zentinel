#!/usr/bin/env python
# encoding: utf-8

"""
event_manager.py

Event Manager

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
from event import Event
from event_queue import EventQueue
import redis
from optparse import OptionParser
import time
import logging
import signal
import traceback
#import ujson
from rq import Queue

sys.path.insert(0, '../')

import web.settings
setup_environ(web.settings)

logger = logging.getLogger('web')

parser = OptionParser(description='Startup options')
# parser.add_option('--redis','-r',dest='redisIP',help='Redis server IP Address',metavar='REDIS',default='192.168.0.98')
parser.add_option('--redis','-r',dest='redisIP',help='Redis server IP Address',metavar='REDIS',default=web.settings.REDIS_IP)
parser.add_option('--redisdb','-d',dest='redisDB',help='Redis server DB',metavar='REDIS_DB',default=.settings.REDIS_DB)

(options, args) = parser.parse_args()

CONSUMED_EVENTS = 'CONSUMED_EVENTS'


class EventManager():
	"""
	This class has a EventQueue and consumes it.
	"""
	def __init__(self):
		self.equeue = EventQueue()
		self.current_event = None

		self.wqueue = self.setup_wqueue()

	def setup_wqueue(self):
		redis_conn = Redis()
		q = Queue(connection=redis_conn)
	
	def consume_queue(self):
		''' Consumes an event and decides if it should be executed '''
		
		t0 = time.time()
		logger.info("Waiting for events to arrive...")
		self.current_event = equeue.pop_event()

		try:
			action = self.current_event.get_action()

			logger.info("Event processed in {0} seconds".format(time.time()-t0))
			logger.debug("Action: {0}".format(action)

			if action:
				self.wqueue.enqueue(action.execute)
			else:
				pass
				# Event discarded

		except Exception:
			logger.error("Failed processing event: {0} Data is {1}".format(traceback.format_exc(),event))
			logger.error("Sending data back to queue...")
			try:
				equeue.push_event(self.current_event)
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
			event_manager.equeue.push_event(event_manager.current_event)			
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