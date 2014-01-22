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

	def __init__(self, event_dict, **kwargs):
		for key,value in event_dict.iteritems():
			setattr(self, key, value)
		for key in kwargs:
			setattr(self, key, kwargs[key])

	def __str__(self):
		return str(self.__dict__)

	def get_data(self):
		return self.__dict__		

	def get_action(self):
		# TODO Check some service or whatever
		# (action_type,params) = getActionTypeForThisEvent(self)
		(action_type,params) = ('SimpleCall',{'ddi':695624167,'cli':666666666,'retries':3})
		# Create object of type 'action_type'
		action = Action.subclass()[action_type](self.get_data(),params)

		return action

	def incr_step(self):
		self.step += 1

	def save(self):
		print 'Event saved: {0}'.format(self)


class Action(object):
	''''
	Represents the action taken for a given event. It's an abstract class and should not be instantiated directly.
	Provides the attribs and public methods execute() and callback()
	'''

	# Creates attributes from dict and keywords. Flexible but obscure. I'm not using it
	"""
	def __init__(self, *event_dict, **kwargs):
		for key in event_dict:
			setattr(self, key, event_dict[key])
		for key in kwargs:
			setattr(self, key, kwargs[key])
	"""
	def __init__(self, event_data, params):
		# FIXME Store an object has no sense, as it's going to be serialized in Redis, losing the reference (see pickle)
		self.event_data = event_data
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
		Quite useful when adding Action subclasses, because you don't need to 
		change anything, just add the subclass '''
		return dict((subclass.__name__, subclass) for subclass in Action.__subclasses__())

	def get_data(self):
		return str(self)		

	def execute(self):
		logger.debug('Execution started...')
		result = self.action()
		self.callback(result)

	def action(self):
		pass

	def callback(self,result):
		print 'Callback {0}'.format(result)
		self.event_data['end_date'] = datetime.utcnow()
		
		if result:
			# success
			vent = Event(self.event_data)
			self.event.save()
		else:
			logger.warning("Action execution failed. Pushing back event to EVENT_QUEUE")
			# Push back on EventQueue
			q = EventQueue()
			event = Event(self.event_data)
			# Increment event step
			event.incr_step()
			q.push_event(event)
			#q.push_event(self.event)

# Subclasses

class SimpleCall(Action):
	"""
	Represents a simple call through Asterisk. 
	Place a call to 'ddi' from 'cli' for 'duration' seconds, and retries 'retries' times
	Inherits from Action, so execute() and callback() are implemented.
	"""
	def __init__(self, event_data, params=None):
		Action.__init__(self, event_data, params)
		self.action_type = self.__class__.__name__
		self.description = 'Make a call until the called party answers or hung up'

	def action(self):
		import random
		result = None
		# Some blocking execution
		time.sleep(5)
		if random.random() > 0.5:
			print 'True - Simple Call'
			result = True
		else:
			print 'False - Simple Call'
			result = False  

		return result


class AcknoweledgedCall(Action):
	"""
	Represents an acknowledged call through Asterisk. 
	Place a call to 'ddi' from 'cli' until the called party sends back 'pin' through DTMF, and retries 'retries' times
	Inherits from Action, so execute() and callback() are implemented.
	"""
	def __init__(self, event_data, params=None):
		Action.__init__(self, event_data, params)
		self.action_type = self.__class__.__name__
		self.description = 'Make a call until the called party dials the given pin, using DTMF tones'

	def action(self):
		import random
		# Some blocking execution
		result = None
		time.sleep(5)
		if random.random() > 0.5:
			print 'True - ACK Call'
			result = True
		else:
			print 'False - ACK Call'
			result = False  

		return result


class AnnounceCall(Action):
	"""
	Represents an call through Asterisk that reads the message. 
	"""
	def __init__(self, event_data, params=None):
		Action.__init__(self, event_data, params)
		self.action_type = self.__class__.__name__
		self.description = 'Make a call until the called party answers. The message in the event is read by a synthetic voice.'

	def action(self):
		import random
		result = None
		# Some blocking execution
		time.sleep(5)
		if random.random() > 0.5:
			print 'True - Annouce Call'
			result = True
		else:
			print 'False - Annouce Call'
			result = False  

		return result
