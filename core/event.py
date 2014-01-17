#!/usr/bin/env python
# encoding: utf-8

"""
event.py

Event

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
import logging
from datetime import datetime
sys.path.insert(0, '../')

logger = logging.getLogger('web')

class Event():
	"""
	Represents a client event
	"""

	"""
	def __init__(self, *event_dict, **kwargs):
		for key in event_dict:
			setattr(self, key, event_dict[key])
		for key in kwargs:
			setattr(self, key, kwargs[key])
	"""
	def __init__(self):
		self.id = None
		self.start_date = utcnow()
		self.process_date = None
		self.end_date = None
		self.client = None
		self.tag = None
		self.step = None

	def __str__(self):
		return str(self.__dict__)

	def get_data(self):
		return str(self)		

	def get_action(self):
		# Check some service or whatever
		# (action_type,params) = getActionTypeForThisEvent(self)

		# Create object of type 'action_type'
		action = Action.subclass()[action_type](self,params)

		return action

	def incr_step(self):
		self.step += 1