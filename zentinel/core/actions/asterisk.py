"""
asterisk.py

Originate a call from an Asterisk server throug the manager interface.
The arguments are extension that should be configured in Asterisk to avoid
toll fraud.

Usage: asterisk.py

Created by Carlos Garcia on 2014-01-25.
Copyright (c) 2010 Pogona. All rights reserved.
"""
from zentinel import settings
from zentinel.core import logger

import httplib
import urllib
import xml.dom.minidom
import signal


# Session cookie specification
COOKIE_NAME = "mansession_id"

# Interface possible values: /rawman, /mxml, /manager
# Possible actions and responses: http://www.voip-info.org/wiki/view/Asterisk+manager+API
LOGIN_REQUEST = "/manager?action=Login&username={0}&secret={1}"
LOGOFF_REQUEST = "/manager?action=Logoff"
SIMPLE_CALL_REQUEST = "/mxml?action=originate&channel=Local/666666@from-zentinel&application=Wait"
ANNOUNCE_CALL_REQUEST = "/mxml?action=originate&channel=Local/666666@from-zentinel&extension=123&context=announce-call&priority=1"


# Defines a C-like struct for Servers
class AsteriskServer:	
  def __init__(self,**kwds):
	self.__dict__.update(kwds)

class AsteriskAMI(object):
	def __init__(self):
		self.AsteriskServersList = []
		self.init_servers()

	# Gets the authentication cookie
	def get_auth_cookie(self,response):
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
			raise Exception

	# Definition of asterisk servers to be monitored and database server
	def init_servers(self):
		for server in settings.ASTERISK_AMI_SERVERS:
			self.AsteriskServersList.append(AsteriskServer(host=server['host'],port=server['port'],user=server['user'],passwd=server['passwd']))
		logger.info("Servers initialized")

	def handle_response(self,response):
		success = False
		logger.debug('Handling response...')
		try:
			xmldoc = response.read()
			xmldoc = xmldoc.rstrip("\r\n ")
			xml_response = xml.dom.minidom.parseString(xmldoc)
			logger.debug(xml_response.toprettyxml())
			if xml_response.getElementsByTagName("generic")[0].attributes["response"].value == "Success":
				success = True
		except:
			logger.error("Response handling failed. Response: ".format(xmldoc ) )
		finally:
			logger.debug('Asterisk response handling successful. Return {0}'.format(success))
			return success

	def send_call(self,request):
		success = False

		for AsteriskServer in self.AsteriskServersList:
			#Authenticates to the server prior to sending the requests
			logger.info("Trying HTTP connection to AMI {0}".format(AsteriskServer))
			conn = httplib.HTTPConnection(AsteriskServer.host,port=AsteriskServer.port)
			try:
				logger.debug('Login Request: ' + LOGIN_REQUEST.format(AsteriskServer.user,AsteriskServer.passwd) )
				conn.request("GET",LOGIN_REQUEST.format(AsteriskServer.user,AsteriskServer.passwd))
				response = conn.getresponse()
				logger.debug('Login Response: {0}'.format(response.read() ) )
				logger.debug("Getting auth cookie...")
				auth_cookie = self.get_auth_cookie(response)
			except Exception:
				logger.error("Cannot connect to Asterisk server {0}".format(AsteriskServer.host))
				break # Pass to next server, or return false
			else:
				logger.info("Connected to Asterisk server {0}".format(AsteriskServer.host))
				conn.request('GET', request, None, auth_cookie)
				logger.debug("Call request made. Request: {0}".format(request) )
				response = conn.getresponse()
				#Handle response
				success = self.handle_response(response)
				break
			finally:
				logger.info("Disconnecting from Asterisk server {0}".format(AsteriskServer.host))
				conn.close()
		return success

	def simple_call(self, ddi, cli, duration, retries ):
		# Setting vars for request
		variables = 'variable=DDI={0},'.format(ddi) +\
					'CLI={0},'.format(cli) +\
					'DURATION=30,' +\
					'RETRIES={0}'.format(retries)
		timeout = 'data=1'

		request = '&'.join([SIMPLE_CALL_REQUEST,timeout,variables])

		return self.send_call(request)


	def announce_call(self, ddi, cli, duration, retries, message , lang):
		# Setting vars for request
		variables =	'variable=DDI={0},'.format(ddi) +\
					'CLI={0},'.format(cli) +\
					'MESSAGE="{0}",'.format(urllib.quote_plus(message)) +\
					'DURATION=60,'.format(duration) +\
					'LANG={0},'.format(lang) +\
					'RETRIES={0}'.format(retries)
		timeout = 'data={0}'.format(duration)

		request = '&'.join([ANNOUNCE_CALL_REQUEST,timeout,variables])

		return self.send_call(request)

	def acknowledged_call(self, ddi, cli, duration, retries, message, lang):
		# Setting vars for request
		variables =	'variable=DDI={0},'.format(ddi) +\
					'CLI={0},'.format(cli) +\
					'MESSAGE="{0}",'.format(urllib.quote_plus(message)) +\
					'DURATION=60,'.format(duration) +\
					'LANG={0},'.format(lang) +\
					'RETRIES={0}'.format(retries)
		timeout = 'data={0}'.format(duration)

		request = '&'.join([ANNOUNCE_CALL_REQUEST,timeout,variables])

		return self.send_call(request)


# Handles the TERM signal (triggered by keyboard or kill command)
def signalHandler(signum, frame):
	logger.debug("Caught signal" + str(signum))
	raise KeyboardInterrupt

signal.signal(signal.SIGTERM, signalHandler)

if __name__ == '__main__':
	logger.debug("Testing unit")
	ami = AsteriskAMI()
	
	data = {}
	data['ddi'] = 695624167
	data['cli'] = 666666666
	data['duration'] = 100
	data['retries'] = 1
	#data['message'] = urllib.quote_plus('Hello Charles')
	data['message'] = urllib.quote_plus("Pacific Rim is a 2013 American science fiction monster film directed by Guillermo del Toro, written by del Toro and Travis Beacham, and starring Charlie Hunnam, Idris Elba, Rinko Kikuchi, Charlie Day, Robert Kazinsky, Max Martini, and Ron Perlman. The film is set in the 2020s, when Earth is at war with the Kaijus,[note1 1] colossal monsters which have emerged from an interdimensional portal on the floor of the Pacific Ocean. To combat the monsters, humanity unites to create the Jaegers [note2 1] : gigantic humanoid mecha, each controlled by at least two pilots, whose minds are joined by a neural bridge. Focusing on the war's later days, the story follows Raleigh Becket, a washed-up Jaeger pilot called out of retirement and teamed with rookie pilot Mako Mori as part of a last-ditch effort to defeat the Kaijus.")
	
	ami.simple_call(data)