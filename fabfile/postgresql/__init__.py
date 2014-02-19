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
	python_package_ensure_pip('psycopg2')

def install():
	package_ensure('postgresql')
	package_ensure('libpq-dev')

def configure():
	init_service()
	logrotate()
	setup()

def deploy():
	prerequisites()
	install()
	configure()