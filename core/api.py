#!/usr/bin/env python
# encoding: utf-8

"""
api.py

Rest API

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""

from flask import Flask,render_template,jsonify,make_response,request
from zen_event import Event
from event_queue import EventQueue
from optparse import OptionParser
import time
import logging
import signal
import traceback
import sys
#import ujson
from redis import Redis
from datetime import datetime

sys.path.insert(0, '../')
import web.settings

logger = logging.getLogger('core')


CONSUMED_EVENTS = 'CONSUMED_EVENTS'

class API(object):
	def __init__(self):
		self.equeue = EventQueue()
		self.current_events = {} # Dict to hold the current events, to avoid duplicates	
		# TODO Implement current_events in redis, so we can run multiple instances
	
	def get_clients(self):
		# TODO Implement a real lookup
		return {'1':{'client': 'Carla', 'service':'SimpleCall'},
				'2':{'client': 'Lucia', 'service':'AcknowledgedCall'},
				'3':{'client': 'David', 'service':'AnnounceCall'},
				}

	def is_client(self,client_key):
		# TODO Implement this for real
		if client_key in self.get_clients().keys():
			return self.get_clients()[client_key]['client']
		else:
			return None

	def handle_event(self,data):
		''' Validates event, and if it's ok dispatchs
		Returns:
		 * Event accepted. Bool
		 * Description. String
		'''
		# Validate event

		# TODO Check if client has credit and so
		# if client ok
		#	go on
		# else
		#	return (False, "not enough credit")

		event = Event(	client = data['client'],\
						message = data['message'],\
						tag = data['tag'],\
						ip_addr = data['ip_addr']	)

		# TODO Better store current_events in redis, so we can have several handlers
		# Check against self.current_events
		if event.get_hash() in self.current_events:
			return (False,'Event repeated')
		else:
			# Add to current events
			self.current_events[event.get_hash()] = event

		# Dispatch event
		self.equeue.push_event(event)

		return (True,event.get_hash())
	

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
	
	client = api_manager.is_client(client_key)
	if not client:
		return make_response(jsonify( {'error': 'Forbbiden', 'description': 'Client does not exist'}),403)

	new_event = {	'client': client,
					'message': message,
					'tag': tag,
					'ip_addr': request.remote_addr,
				}

	(valid,data) = api_manager.handle_event(new_event)				
	if valid:
		return make_response(jsonify( {'event_id': str(data)} ),200)
	else:
		return make_response(jsonify( {'error': 'Forbbiden', 'description': str(data)}),403)
	
if __name__ == '__main__':
	
	signal.signal(signal.SIGTERM, __signalHandler)
	signal.signal(signal.SIGINT, __signalHandler)

	api_manager = API()
	api_server.run(debug = web.settings.DEBUG)