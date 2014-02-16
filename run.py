#!env/bin/python
from zentinel.web import web
from zentinel.settings import WEB_IPADDR,WEB_PORT


web.run(debug = True,host=WEB_IPADDR,port=WEB_PORT)
