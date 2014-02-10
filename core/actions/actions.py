#!/usr/bin/env python
# encoding: utf-8

"""
actions.py

Action classes

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
import logging
import time
from datetime import datetime
from event_queue import EventQueue
from zen_event import Event
import hashlib
import asterisk

logger = logging.getLogger('core')

class Action(object):
	''''
	Represents the action taken for a given event. It's an abstract class and should not be instantiated directly.
	Provides the attribs and public methods execute() and callback()
	'''
	def __init__(self, event_data):
		self.event_data = event_data # Store a dict instead of object, to allow modification
		self.action_type = self.__class__.__name__

	def __str__(self):
		return str(self.__dict__)

	def init_attrbs(self, attrs, values):
		for attr in attrs:
			if attr in values.keys():
				setattr(self, attr, values[attr])
			else:
				logger.critical("Action can't be created. Missing attribute {0}".format(attr))
				return False
		return True

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
		self.event_data['execution_date'] = datetime.utcnow()
		result = self.action()
		self.callback(result)

	def action(self):
		pass

	def callback(self,result):
		self.event_data['end_date'] = datetime.utcnow()
		self.event_data['step'] += 1
		event = Event.from_dict(self.event_data)
		if result:
			# success 
			# event.save()
			pass
		else:
			logger.warning("Action execution failed. Pushing back event to EVENT_QUEUE")
			# Push back Event on EventQueue
			q = EventQueue()
			q.push_event(event)

# Subclasses

class SimpleCall(Action):
	"""
	Represents a simple call through Asterisk. 
	Place a call to 'ddi' from 'cli' for 'duration' seconds, and retries 'retries' times
	Inherits from Action, so execute() and callback() are implemented.
	"""
	def __init__(self, event_data, values):
		Action.__init__(self, event_data)
		self.action_type = self.__class__.__name__
		self.description = 'Make a call until the called party answers or hung up'

		# List of attributes for this kind of action
		attrs = ['ddi','cli','retries','duration']

		if not self.init_attrbs(attrs, values):
			return None

	def action(self):
		logger.debug("Executing Simple Call Action")
		result = None
		ami = asterisk.AsteriskAMI()
		result = ami.simple_call(ddi=self.ddi, cli=self.cli, retries=self.retries, duration=self.duration)
		
		return result


class AcknoweledgedCall(Action):
	"""
	Represents an acknowledged call through Asterisk. 
	Place a call to 'ddi' from 'cli' until the called party sends back 'pin' through DTMF, and retries 'retries' times
	Inherits from Action, so execute() and callback() are implemented.
	"""
	def __init__(self, event_data, values):
		Action.__init__(self, event_data)
		self.action_type = self.__class__.__name__
		self.description = 'Make a call until the called party dials the given pin, using DTMF tones'

		# List of attributes for this kind of action
		attrs = ['ddi','cli','retries','duration','pin','lang']

		if not self.init_attrbs(attrs, values):
			return None

	def action(self):
		logger.debug("Executing Acknowledged Call Action")
		result = None
		ami = asterisk.AsteriskAMI()
		result = ami.acknowledged_call(ddi=self.ddi, cli=self.cli, retries=self.retries, duration=self.duration)
		
		return result


class AnnounceCall(Action):
	"""
	Represents an call through Asterisk that reads the message. 
	"""
	def __init__(self, event_data, values):
		Action.__init__(self, event_data)
		self.action_type = self.__class__.__name__
		self.description = 'Make a call until the called party answers. The message in the event is read by a synthetic voice.'

		# List of attributes for this kind of action
		attrs = ['ddi','cli','retries','lang','message','duration']

		if not self.init_attrbs(attrs, values):
			return None


	def action(self):
		logger.debug("Executing Announce Call Action")
		result = None
		ami = asterisk.AsteriskAMI()
		result = ami.announce_call(ddi=self.ddi, cli=self.cli, retries=self.retries, duration=self.duration, lang=self.lang, message=self.message)
		
		return result
