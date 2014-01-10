#!env/bin/python
from app import app
from config import IPADDR,PORT


app.run(debug = True,host=IPADDR,port=PORT)
