#!/usr/bin/env python
# encoding: utf-8

"""
event.py

Event

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
import logging
import time
from datetime import datetime
import hashlib

logger = logging.getLogger('core')

class Event():
	"""
	Represents a client event
	"""

	def __init__(self, client_key, ip_addr, message='', tag=None, reception_date=datetime.utcnow(), execution_date=None, end_date=None, step=0):
		"""
		Creates an Event object from parameters
		"""
		self.client_key = client_key
		self.message = message
		self.tag = tag
		self.ip_addr = ip_addr
		self.reception_date = reception_date
		self.execution_date = execution_date
		self.end_date = end_date
		self.step = step

	@classmethod
	def from_dict(self,data):
		"""
		Creates an Event object from dict. Data must be sanitized!
		Used only when re-creating Event from EventQueue
		"""
		attrs = ['client_key', 'message' ,'tag', 'ip_addr', 'reception_date', 'execution_date', 'end_date', 'step']
		
		dict_sane = True
		for attr in attrs:
			if attr not in data:
				dict_sane = False
				break

		if dict_sane:
			logger.debug("Event generated from dict: {0}".format(self))
			return Event(
				client_key = data['client_key'],\
				message = data['message'],\
				tag = data['tag'],\
				ip_addr = data['ip_addr'],\
				reception_date = data['reception_date'],\
				execution_date = data['execution_date'],\
				end_date = data['end_date'],\
				step = data['step'],\
				)
		
			
	def __str__(self):
		return str(self.__dict__)

	def get_data(self):
		return self.__dict__		

	def get_hash(self):
		# Get a uniqueid based in some attributes
		data = ''.join([self.client_key,self.message,self.tag,str(self.step)])
		return hashlib.sha256(str(data)).hexdigest()

	def save(self):
		# TODO Implement a real save
		print 'Event saved: {0}'.format(self)