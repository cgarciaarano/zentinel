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
	def __init__(self,data):
		self.id = None
		self.start_date = datetime.utcnow()
		self.process_date = None
		self.end_date = None
		self.client = data['client']
		self.message = data['message']
		self.ip_addr = data['ip_addr']
		self.tag = data['tag']
		self.step = 1

	def __str__(self):
		return str(self.__dict__)

	def get_data(self):
		return str(self)		

	def get_action(self):
		# Check some service or whatever
		# (action_type,params) = getActionTypeForThisEvent(self)
		(action_type,params) = ('SimpleCall',{'ddi':695624167,'cli':666666666,'retries':3})
		# Create object of type 'action_type'
		action = Action.subclass()[action_type](self,params)

		return action

	def incr_step(self):
		self.step += 1


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

	def __init__(self, event, params):
		self.event = event
		self.action_type = self.__class__.__name__
		self.params = params

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
		Action.__init__(self, event, params)
		self.action_type = self.__class__.__name__

	def execute(self):
		import random
		# Some blocking execution
		time.sleep(5)
		if random.random() > 0.5:
			print 'True'
			result = True
		else:
			print 'False'
			result = False  

		self.callback(result)


class AcknoweledgedCall(Action):
	"""
	Represents an acknowledged call through Asterisk. 
	Place a call to 'ddi' from 'cli' until the called party sends back 'pin' through DTMF, and retries 'retries' times
	Inherits from Action, so execute() and callback() are implemented.
	"""
	def __init__(self, event, params=None):
		Action.__init__(self, event, params)
		self.action_type = self.__class__.__name__

	def execute(self):
		# Some blocking execution
		time.sleep(10)
		result = True 

		self.callback(result)


class AnnounceCall(Action):
	"""
	Represents an call through Asterisk that reads the message. 
	"""
	def __init__(self, event, params=None):
		Action.__init__(self, event, params)
		self.action_type = self.__class__.__name__

	def execute(self):
		# Some blocking execution
		sys.sleep(10)
		result = True 

		self.callback(result)
