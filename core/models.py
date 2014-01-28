#!/usr/bin/env python
# encoding: utf-8

"""
models.py

Event

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
import logging
import time
from datetime import datetime
from event_queue import EventQueue
import hashlib
from actions import asterisk, actions

logger = logging.getLogger('web')

class Event():
	"""
	Represents a client event
	"""

	def __init__(self, event_dict, **kwargs):
		"""
		Creates an object, based in dict passed as parameter. Quite obscure.

		Example dict:
		event = {	'client': client,
					'message': message,
					'tag': tag,
					'ip_addr': request.remote_addr,
					'reception_date': datetime.utcnow(),
					'execution_date': None,
					'end_date': None,
					'step':0,
			}
		"""
		for key,value in event_dict.iteritems():
			setattr(self, key, value)
		for key in kwargs:
			setattr(self, key, kwargs[key])

	def __str__(self):
		return str(self.__dict__)

	def get_data(self):
		return self.__dict__		

	def get_hash(self):
		# Get a uniqueid based in some attributes
		data = ''.join([self.client,self.message,self.tag,str(self.step)])
		return hashlib.sha256(str(data)).hexdigest()

	def get_action(self):
		# TODO Check some service or whatever
		# (action_type,params) = getActionTypeForThisEvent(self)
		(action_type,params) = ('SimpleCall',{'ddi':695624167,'cli':666666666,'retries':3,'duration':1})
		# Create object of type 'action_type'
		action = actions.Action.subclass()[action_type](self.get_data(),params)

		return action

	def save(self):
		# TODO Implement a real save
		print 'Event saved: {0}'.format(self)