"""
api.py

Rest API Manager

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
from zentinel.core.zen_event import Event
from zentinel.core.utils import  event_queue, shared_mem
from zentinel.core import logger
from zentinel.web import models, db

class API(object):
	def __init__(self):
		logger.debug("Creating API object")
		self.equeue = event_queue
		self.current_events = shared_mem

	def get_clients(self):
		return models.Client.query.all()

	def is_client(self,client_key):
		logger.debug('Checking client with key {0}'.format(client_key))
		return models.Client.query.filter(models.Client.client_key == client_key).scalar().name

	def handle_event(self,data):
		''' Validates event, and if it's ok dispatchs
		Returns:
		 * Event accepted. Bool
		 * Description. String
		'''
		# Validate event
		client = self.is_client(data['client_key'])
		if not client:
			return (False,'Client does not exist')
		# TODO Check if client has credit and so
		# if client ok
		#	go on
		# else
		#	return (False, "not enough credit")

		event = Event(	client_key = data['client_key'],\
						message = data['message'],\
						tag = data['tag'],\
						ip_addr = data['ip_addr']	)

		# Check against self.current_events
		logger.debug('Checking if event is repeated')
		if self.current_events.exists(event.get_hash()):
			return (False,'Event repeated')
		else:
			# Add to current events
			self.current_events.set(event.get_hash(),event)

		# Dispatch event
		logger.debug('All tests passed. Dispatching event.')
		self.equeue.push_event(event)

		return (True,event.get_hash())