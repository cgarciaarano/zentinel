"""
views.py

Rest API views

2014 Pogona 

@author Carlos Garcia <cgarciaarano@gmail.com>
"""
from zentinel.core.api import api_server, api_manager
from zentinel.core import logger

from flask import jsonify,make_response,request

import signal
import sys

# Server implementation
@api_server.route('/api/<client_key>/<message>/<tag>')
def new_event(client_key,message,tag):
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

@api_server.errorhandler(500)
def error(error):
		return make_response(jsonify( { 'error': 'Server error' } ), 500)

@api_server.errorhandler(403)
def forbidden(error):
		return make_response(jsonify( { 'error': 'Forbidden' } ), 404)

@api_server.errorhandler(404)
def notfound(error):
		return make_response(jsonify( { 'error': 'URL not found' } ), 404)

def signal_handler(signum, frame):

	logger.debug("Caught signal" + str(signum))
	logger.info("Exiting now")
	sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)