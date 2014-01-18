#!/usr/bin/env python
# encoding: utf-8

"""
action.py

Action

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
import logging
from event_queue import EventQueue
from datetime import datetime

logger = logging.getLogger('web')

class Action(object):
	''''
	Represents the action taken for a given event. It's an abstract class and should not be instantiated directly.
	Provides the attribs and public methods execute() and callback()
	'''

	# Creates attributes from dict and keywords. Flexible but obscure
	def __init__(self, *event_dict, **kwargs):
		for key in event_dict:
			setattr(self, key, event_dict[key])
		for key in kwargs:
			setattr(self, key, kwargs[key])

	def __init__(self, event):
		self.event = event
		self.action_type = self.__class__.__name__

	def __str__(self):
		return str(self.__dict__)

	def get_type(self):
		return self.action_type

	@staticmethod
	def subclass():
		''' Returns a dict with all subclasses names and instances.
		P.e. {'SimpleCall': SimpleCall, 'AcknowledgedCall': AcknowledgedCall}.
		Quite useful when adding Actions ;) '''
		return dict((subclass.__name__, subclass) for subclass in Action.__subclasses__())

	def get_data(self):
		return str(self)		

	def execute(self):
		pass

	def callback(self,result):
		if result:
			# success
			pass
		else:
			# Increment event step
			self.event.incr_step()
			
			# Push back on EventQueue
			q = EventQueue()
			q.push_event(self.event)

# Subclasses

class SimpleCall(Action):
	"""
	Represents a simple call through Asterisk. 
	Place a call to 'ddi' from 'cli' for 'duration' seconds, and retries 'retries' times
	Inherits from Action, so execute() and callback() are implemented.
	"""
	def __init__(self, event, params=None):
		Action.__init__(self, event)
		self.action_type = self.__class__.__name__
		self.params = params

	def execute(self):
		# Some blocking execution
		result = True 

		self.callback(result)


class AcknoweledgedCall(Action):
	"""
	Represents an acknowledged call through Asterisk. 
	Place a call to 'ddi' from 'cli' until the called party sends back 'pin' through DTMF, and retries 'retries' times
	Inherits from Action, so execute() and callback() are implemented.
	"""
	self.action_type = self.__class__.__name__
	
	def __init__(self, event, params=None):
		Action.__init__(self, event)
		self.action_type = self.__class__.__name__
		self.params = {	ddi: None,
						cli: None,
						pin: None,
					}

	def execute(self):
		# Some blocking execution
		result = True 

		self.callback(result)


class AnnounceCall(Action):
	"""
	Represents an call through Asterisk that reads the message. 
	"""
	self.action_type = self.__class__.__name__
	
	def __init__(self, event, params=None):
		Action.__init__(self, event)
		self.action_type = self.__class__.__name__
		self.params = {	ddi: None,
						cli: None,
						retries: None,
						message: None,
						language: None
					}

	def execute(self):
		# Some blocking execution
		result = True 

		self.callback(result)