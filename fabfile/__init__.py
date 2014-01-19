#!/usr/bin/env python
# encoding: utf-8

from fabric.api import *
from fabric.contrib.console import confirm
from cuisine import *
import os
import sys
from fabric.colors import red, green

env.user = 'vagrant'
env.password = 'vagrant'

PROJECT_ROOT = '/vagrant'
ENV_ROOT = '/home/vagrant'

users = {	'cgarcia':'cgarcia',
			'jvizcaino':'jvizcaino',
		}

# System stuff
def addUsers():
	for user,passwd in users.iteritems():
		user_ensure(user,passwd)
		group_user_ensure('sudo',user)

def install_redis():
	package_ensure('python-software-properties')
	sudo('add-apt-repository ppa:chris-lea/redis-server')
	package_update()
	package_ensure('redis-server')

@task
def setup_system():
	addUsers()

@task
def configure_system():
	install_redis()
	package_update()
	package_ensure('curl')
	package_ensure('asterisk')

# Application stuff
@task
def app_environment():
	# BROKEN
	# Dont work in Windows
	# with cd(PROJECT_ROOT):
		if not dir_exists('{0}/env/'.format(ENV_ROOT)):
			sudo('wget https://raw.github.com/pypa/virtualenv/1.9.X/virtualenv.py')
			sudo('python virtualenv.py {0}/env/'.format(ENV_ROOT))
			sudo('env/bin/pip install -r {0}/requirements.txt'.format(PROJECT_ROOT))

def python_requisites():
	# This should be in requisites.txt
	python_package_ensure_pip('redis')
	python_package_ensure_pip('rq')
	python_package_ensure_pip('Flask')

def prerequisites():
	package_ensure('python-dev')
	package_ensure('libevent-dev')
	python_requisites()

@task
def deploy():
	prerequisites()
	app_environment()
