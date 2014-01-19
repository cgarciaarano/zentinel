#!/usr/bin/env python
# encoding: utf-8

"""
api.py

Rest API

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""

from flask import Flask,render_template,jsonify,make_response,request
from models import Event
from event_queue import EventQueue
from optparse import OptionParser
import time
import logging
import signal
import traceback
import sys
#import ujson
from redis import Redis
import hashlib

logger = logging.getLogger('core')


CONSUMED_EVENTS = 'CONSUMED_EVENTS'

class API(object):
	def __init__(self):
		self.equeue = EventQueue()
		self.current_events = {} # Dict to hold the current events, to avoid duplicates	
		# TODO Implement current_events in redis, so we can run multiple instances
	
	def get_clients(self):
		return {'1':'Pepe',
				'2':'Lucia',
				'3':'David',
				}

	def handle_event(self,data):
		''' Validates event, and if it's ok creates it and dispatchs
		Returns:
		 * Event accepted. Bool
		 * Event or description of rejection. Event or String
		'''
		# Validate event
		
		# Check client
		if data['client_key'] in self.get_clients().keys():
			data['client'] = self.get_clients()[data['client_key']]
		else:
			return (False,'Client does not exist')
		
		# Make hash
		hash = hashlib.sha256(str(data)).hexdigest()
		# Check against self.current_events
		if hash in self.current_events:
			return (False,'Event repeated')
		else:
			# Add to current events
			self.current_events[hash] = data 

		event = Event(data)

		# Dispatch event
		self.equeue.push_event(event)

		return (True,event)
	

	def run(self):
		while True:
			self.consume_queue()


def __signalHandler(signum, frame):

	logger.debug("Caught signal" + str(signum))
	logger.info("Exiting now")
	sys.exit(0)


# Server implementation
api_server = Flask(__name__)

@api_server.route('/api/<client_key>/<message>/<tag>')
def new_event(client_key,message,tag):
	new_event = {	'client_key': client_key,
					'message': message,
					'tag': tag,
					'ip_addr': request.remote_addr,
				}

	(valid,data) = api_manager.handle_event(new_event)				
	if valid:
		return make_response(jsonify( {'event': str(data)} ),200)
	else:
		return make_response(jsonify( {'error': 'Forbbiden', 'description': str(data)}),403)
	
if __name__ == '__main__':
	
	signal.signal(signal.SIGTERM, __signalHandler)
	signal.signal(signal.SIGINT, __signalHandler)

	api_manager = API()
	api_server.run(debug = True)

