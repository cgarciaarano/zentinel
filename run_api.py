#!env/bin/python
from zentinel.core.api import api_server
from zentinel.settings import API_IPADDR,API_PORT

api_server.run(debug = True,host=API_IPADDR,port=API_PORT)