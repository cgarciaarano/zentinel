#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8

"""
alert_call.py

Originate a call from an Asterisk server throug the manager interface.
The arguments are extension that should be configured in Asterisk to avoid
toll fraud.

Usage: alert_call.py <username> notUsed notUsed

There are arguments not used, because they are sent by Zabbix automatically

Created by Carlos Garcia on 2010-11-07.
Copyright (c) 2010 StoneWorkSolutions. All rights reserved.
"""

import httplib
import logging
import logging.handlers
import xml.dom.minidom
import time
import os
import sys
import signal

sys.path.insert(0, '../')
import web.settings

logger = logging.getLogger('core')

# Session cookie specification
COOKIE_NAME = "mansession_id"

TIMEOUT = 5

# Request the channel list, possible values: /rawman, /mxml, /manager
# Possible actions and responses: http://www.voip-info.org/wiki/view/Asterisk+manager+API
CHANNELS_REQUEST = "/asterisk/mxml?action=status"
LOGOFF_REQUEST = "/asterisk/manager?action=Logoff"

################## Utilities #####################
def AsteriskAMI(object):
    def __init__(self):

# Gets the authentication cookie
def getAuthCookie(response):
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


# Handles the TERM signal (triggered by keyboard or kill command)
def signalHandler(signum, frame):
    logger.debug("Caught signal" + str(signum))
    raise KeyboardInterrupt

# Defines a C-like struct for Servers
class AsterServer:
  def __init__(self,**kwds):
    self.__dict__.update(kwds)

# Definition of asterisk servers to be monitored and database server
def initServers():
  for server in web.settings.ASTERISK_AMI_SERVERS:
    astServersList.append(Server(host="62.14.244.106:5080",hostname="Pbx",user=ast_user,passwd=ast_passwd))

signal.signal(signal.SIGTERM, signalHandler)

# For debugging purposes
for arg in sys.argv:
        logger.debug("parameter: " + str(arg))

if len(sys.argv) != 4:
        logger.error("Number of parameters: " + str(len(sys.argv)) + ", which is incorrect. Exiting...")
        sys.exit(1)
else:
        tmp = sys.argv[1].split()
        user = tmp[-1]
        logger.debug("User: " + user)
        CALL_REQUEST = "/asterisk/mxml?action=originate&channel=local/" + user + "@from-zabbix&application=Wait&data=9000"

astServersList = []

initServers()
logger.info("Servers initialized")

for astServer in astServersList:

        #Authenticates to the server prior to sending the requests
        logger.debug("Trying HTTP connection")
        conn = httplib.HTTPConnection(astServer.host)
        try:
                logger.debug("Login in...")
                conn.request("GET","/asterisk/manager?action=Login&username=" + astServer.user + "&secret=" + astServer.passwd)
                response = conn.getresponse()
                logger.debug("Getting auth cookie...")
                auth_cookie = getAuthCookie(response)
        except Exception:
                logger.warning("Cannot connect to Asterisk server " + astServer.hostname)
                conn.close()
                raise
        else:
                logger.debug("Connected to Asterisk server " + astServer.hostname)
                conn.request('GET', CALL_REQUEST, None, auth_cookie)
                logger.debug("Call request made")
                response = conn.getresponse()
                logger.debug("Call placed: " + str(response.read()))
sys.exit(0)