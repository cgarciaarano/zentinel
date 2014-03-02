"""
actions.py

Action classes

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
from zentinel.core.utils import event_queue
from zentinel.core.actions import asterisk
from zentinel.core import logger
from zentinel.web import models
from zentinel import settings

from datetime import datetime
import hashlib

class Action(models.ActionConfig):
	''''
	Represents the action taken for a given event. It's an abstract class and should not be instantiated directly.
	Provides the attribs and public methods execute() and callback()
	'''
	def __init__(self, event_data):
		self.event_data = event_data # Store a dict instead of object, to allow modification
		self.action_type = self.__class__.__name__
		self.message = event_data['message']

	def __str__(self):
		return str(self.__dict__)

	def get_type(self):
		return self.action_type

	@staticmethod
	def subclass():
		''' Returns a dict with all subclasses names and instances.
		P.e. {'SimpleCall': SimpleCall, 'AcknowledgedCall': AcknowledgedCall}.
		Quite useful when adding Action subclasses, because you don't need to 
		change anything, just add the subclass.

		Take in account that there are intermediate subclasses, like ActionCall, that's why there
		is two __subclasses__() calls. '''
		subclasses = {}
		for inter_subclass in Action.__subclasses__():
			for subclass in inter_subclass.__subclasses__():
				subclasses[subclass.__name__] = subclass

		return subclasses
		#return dict((subclass.__name__, subclass) for subclass in Action.__subclasses__().__subclasses__())

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
		event = models.Event.from_dict(self.event_data)
		if result:
			# success 
			# event.save()
			pass
		else:
			logger.warning("Action execution failed. Pushing back event to EVENT_QUEUE")
			# Push back Event on EventQueue
			q = event_queue
			q.push_event(event)

# Subclasses
class ActionCall(Action):
	def __init__(self, event_data):
		Action.__init__(self, event_data)
		self.duration = settings.MAX_CALL_DURATION


class SimpleCall(ActionCall, models.SimpleCallParams):
	"""
	Represents a simple call through Asterisk. 
	Place a call to 'ddi' from 'cli' for 'duration' seconds, and retries 'retries' times
	Inherits from Action, so execute() and callback() are implemented.
	"""
	def __init__(self, event_data):
		ActionCall.__init__(self, event_data)
		self.action_type = self.__class__.__name__
		self.description = 'Make a call until the called party answers or hung up'

	def action(self):
		logger.debug("Executing Simple Call Action")
		result = None
		ami = asterisk.AsteriskAMI()
		result = ami.simple_call(ddi = self.ddi, cli = self.cli, retries = self.retries, duration = self.duration)
		
		return result


class AcknoweledgedCall(ActionCall, models.AcknowledgedCallParams):
	"""
	Represents an acknowledged call through Asterisk. 
	Place a call to 'ddi' from 'cli' until the called party sends back 'pin' through DTMF, and retries 'retries' times
	Inherits from Action, so execute() and callback() are implemented.
	"""
	def __init__(self, event_data):
		ActionCall.__init__(self, event_data)
		self.action_type = self.__class__.__name__
		self.description = 'Make a call until the called party dials the given pin, using DTMF tones'

	def action(self):
		logger.debug("Executing Acknowledged Call Action")
		result = None
		ami = asterisk.AsteriskAMI()
		result = ami.acknowledged_call(ddi = self.ddi, cli = self.cli, retries = self.retries, duration = self.duration)
		
		return result


class AnnounceCall(ActionCall, models.AnnounceCallParams):
	"""
	Represents an call through Asterisk that reads the message. 
	"""
	def __init__(self, event_data):
		ActionCall.__init__(self, event_data)
		self.action_type = self.__class__.__name__
		self.description = 'Make a call until the called party answers. The message in the event is read by a synthetic voice.'


	def action(self):
		logger.debug("Executing Announce Call Action")
		result = None
		ami = asterisk.AsteriskAMI()
		result = ami.announce_call(ddi = self.ddi, cli = self.cli, retries = self.retries, duration = self.duration, lang = self.lang, message = self.message)
		
		return result
