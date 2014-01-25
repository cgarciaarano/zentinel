#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

"""
asterisk.py

Originate a call from an Asterisk server throug the manager interface.
The arguments are extension that should be configured in Asterisk to avoid
toll fraud.

Usage: asterisk.py

Created by Carlos Garcia on 2014-01-25.
Copyright (c) 2010 Pogona. All rights reserved.
"""

import httplib
import logging
import logging.handlers
import xml.dom.minidom
import time
import os
import sys
import signal

sys.path.insert(0, '../../')
import web.settings

logger = logging.getLogger('core')

# Session cookie specification
COOKIE_NAME = "mansession_id"

TIMEOUT = 5

# Request the channel list, possible values: /rawman, /mxml, /manager
# Possible actions and responses: http://www.voip-info.org/wiki/view/Asterisk+manager+API
LOGIN_REQUEST = "/asterisk/manager?action=Login&username={0}&secret={1}"
LOGOFF_REQUEST = "/asterisk/manager?action=Logoff"
CALL_REQUEST = "/asterisk/mxml?action=originate&channel=Local/666666@from-zentinel extension zentinel@from-zentinel"


# Defines a C-like struct for Servers
class AstServer:	
  def __init__(self,**kwds):
	self.__dict__.update(kwds)

class AsteriskAMI(object):
	def __init__(self):
		self.astServersList = []
		self.initServers()

	# Gets the authentication cookie
	def getAuthCookie(self,response):
		# Get headers and cookie value
		try:
			head = response.getheaders()
			for attr in head:
				if attr[0] == "set-cookie" and attr[1].split(";")[0].split("=")[0] == COOKIE_NAME:
					cookieValue = attr[1].split(";")[0].split("=")[1].replace("\"","")
					break
			logger.debug("Authentication success . AuthCookie value: " + COOKIE_NAME + " = " + cookieValue)
			return {"Cookie" : COOKIE_NAME + "=" + cookieValue }
		except:
			logger.error("Cannot get HTTP headers. Authentication failed!")

	# Definition of asterisk servers to be monitored and database server
	def initServers(self):
		for server in web.settings.ASTERISK_AMI_SERVERS:
			self.astServersList.append(AstServer(host=server['host'],port=server['port'],user=server['user'],passwd=server['passwd']))
		logger.info("Servers initialized")


	def simpleCall(self,params):
		success = False
		
		ddi = params['ddi']
		cli = params['cli']
		duration = params['duration']
		retries = params['retries']

		for astServer in self.astServersList:
			#Authenticates to the server prior to sending the requests
			logger.debug("Trying HTTP connection to AMI {0}".format(astServer))
			conn = httplib.HTTPConnection(astServer.host,port=astServer.port)
			try:
				logger.debug("Logging in...")
				conn.request("GET",LOGIN_REQUEST.format(astServer.user,astServer.passwd))
				response = conn.getresponse()
				logger.debug("Getting auth cookie...")
				auth_cookie = self.getAuthCookie(response)
			except Exception:
				logger.warning("Cannot connect to Asterisk server " + astServer.host)
				raise
				conn.close()
			else:
				logger.debug("Connected to Asterisk server " + astServer.host)
				conn.request('GET', CALL_REQUEST, None, auth_cookie)
				logger.debug("Call request made")
				response = conn.getresponse()
				logger.debug("Call placed: " + str(response.read()))
				#TODO Handle response
				success = True
				break

			return success

# Handles the TERM signal (triggered by keyboard or kill command)
def signalHandler(signum, frame):
	logger.debug("Caught signal" + str(signum))
	raise KeyboardInterrupt

signal.signal(signal.SIGTERM, signalHandler)

if __name__ == '__main__':
	logger.debug("Testing unit")
	ami = AsteriskAMI()
	
	data = {}
	data['ddi'] = 123
	data['cli'] = 214125
	data['duration'] = 30
	data['retries'] = 1
	
	ami.simpleCall(data)