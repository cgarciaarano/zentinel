# encoding: utf-8
"""
event_manager.py

Event Manager

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
from zentinel import settings
from zentinel.web import models, db
from zentinel.core import logger
from zentinel.core.utils import event_queue, worker_queue
from zentinel.core.zen_event import Event
from zentinel.core.actions import actions

import sys
import time
import signal
import traceback
#import ujson

class EventManager():
	"""
	This class has a EventQueue and consumes it.
	"""
	def __init__(self):
		logger.debug("Creating Event Manager object")
		self.equeue = event_queue
		self.equeue.reset_counter()
		self.current_event = None
		self.wqueue = worker_queue


		signal.signal(signal.SIGTERM, self.signal_handler)
		signal.signal(signal.SIGINT, self.signal_handler)
	
	def consume_queue(self):
		''' Consumes an event and decides if it should be executed '''
		logger.info("Waiting for events to arrive...")
		self.current_event = self.equeue.pop_event()
		
		t0 = time.time()
		# TODO Max numbers of steps 
		if self.current_event.step < 3:
			try:
				action = self.get_action()

				logger.info("Action decided in {0} seconds".format(time.time()-t0))
				
				if action:
					logger.debug("Action: {0}".format(action))
					self.wqueue.enqueue(action.execute)
					logger.info("Action {0} dispatched".format(action.get_type()))
				else:
					logger.info("Action not definied. Changing step and pushing back to queue")
					self.current_event.step += 1
					self.equeue.push_event(self.current_event)


			except Exception:
				logger.error("Failed processing event: {1}\nException data is:\n{0}".format(traceback.format_exc(),self.current_event))
				logger.error("Sending data back to queue...")
				try:
					self.equeue.push_event(self.current_event)
					logger.info("Data succesfully sent back to queue!")
				except:
					logger.critical("Could not send data back to queue")
					logger.critical(traceback.format_exc())
					sys.exit(-1)
		else:		
			logger.debug("Event step exceeded. Discarding event.")
			# TODO Save discarded event
		
		self.current_event = None

	def get_action(self):
		# TODO Check some service or whatever
		client_key = self.current_event.client_key
		tag = self.current_event.tag
		step = self.current_event.step
		
		action_config = models.Client.query.filter(models.Client.client_key == client_key).first().get_action(tag, step) 
		params = {'ddi':695624167,'cli':666666666,'retries':3,'duration':1,'lang':'es','message':'Lucía es la más bonita del mundo!'}
		logger.debug('Action Config retrieved: {0}'.format(action_config))

		if action_config:
			# Create object of type 'action_type'
			action = actions.Action.subclass()[action_config.action_type](self.current_event.get_data(),params)

			return action

	def run(self):
		while True:
			self.consume_queue()


	def signal_handler(self, signum, frame):

		logger.debug("Caught signal" + str(signum))

		try:
			if self.current_event:
				logger.error("Signal recived while inserting, sending data back to event queue...")

				try:
					self.equeue.push_event(self.current_event)			
					logger.info("Data succesfully sent back to event queue!")
				except:
					logger.error("Can't insert back to event queue")
					logger.error("Event: {0}".format(self.current_event))

		except:
			logger.debug("Something went wrong {0}".format(traceback.format_exc()))
		finally:
			logger.info("Exiting now")
			sys.exit(0)



if __name__ == '__main__':
	event_manager = EventManager()
	event_manager.run()