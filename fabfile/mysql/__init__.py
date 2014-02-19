#!/usr/bin/env python
# encoding: utf-8

from fabric.api import *
from fabric.contrib.console import confirm
from cuisine import *
import os
import sys
from fabric.colors import red, green


def init_service():
	pass

def logrotate():
	pass

def setup():
	pass

def prerequisites():
	pass

def install():
	package_ensure('mysql-server')

def configure():
	init_service()
	logrotate()
	setup()

def deploy():
	prerequisites()
	install()
	configure()