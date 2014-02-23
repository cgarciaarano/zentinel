#!/usr/bin/env python
# encoding: utf-8

"""
api.py

Rest API

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
import sys
sys.path.insert(0, '../../')
# For Debugginf
sys.path.insert(0, '/vagrant')

from zen_event import Event
from zentinel.core import core_utils
from zentinel.web import models, db

from event_queue import EventQueue


from flask import Flask,render_template,jsonify,make_response,request
from optparse import OptionParser
import time
import logging
import signal
import traceback
#import ujson
from redis import Redis
from datetime import datetime

logger = logging.getLogger('core')
api_server = Flask(__name__)

class API(object):
	def __init__(self):
		self.equeue = EventQueue()
		self.current_events = core_utils.SharedMem() 

	def get_clients(self):
		return models.Client.query.all()

	def is_client(self,client_key):
		logger.debug('Checking client with key {0}'.format(client_key))
		return models.Client.query.filter(models.Client.client_key == client_key).scalar().name

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

		event = Event(	client_key = data['client_key'],\
						message = data['message'],\
						tag = data['tag'],\
						ip_addr = data['ip_addr']	)

		# Check against self.current_events
		logger.debug('Checking if event is repeated')
		if self.current_events.exists(event.get_hash()):
			return (False,'Event repeated')
		else:
			# Add to current events
			self.current_events.set(event.get_hash(),event)

		# Dispatch event
		logger.debug('All tests passed. Dispatching event.')
		self.equeue.push_event(event)

		return (True,event.get_hash())


def __signalHandler(signum, frame):

	logger.debug("Caught signal" + str(signum))
	logger.info("Exiting now")
	sys.exit(0)



# Server implementation
@api_server.route('/api/<client_key>/<message>/<tag>')
def new_event(client_key,message,tag):
	
	client = api_manager.is_client(client_key)
	if not client:
		return make_response(jsonify( {'error': 'Forbbiden', 'description': 'Client does not exist'}), 403)

	new_event = {	'client_key': client_key,
					'message': message,
					'tag': tag,
					'ip_addr': request.remote_addr,
				}

	(valid,data) = api_manager.handle_event(new_event)				
	if valid:
		return make_response(jsonify( {'event_id': str(data)} ), 200)
	else:
		return make_response(jsonify( {'error': 'Forbbiden', 'description': str(data)}), 403)

signal.signal(signal.SIGTERM, __signalHandler)
signal.signal(signal.SIGINT, __signalHandler)	
api_manager = API()

if __name__ == '__main__':
	api_server.run(debug = True, port = 8888)