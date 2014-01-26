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

PROJECT_ROOT = '/vagrant/'
ENV_ROOT = '/home/vagrant/'

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

def configure_asterisk():
	with mode_sudo():
		configure_tts()

		file_link(PROJECT_ROOT + 'core/actions/zentinel.ael','/etc/asterisk/zentinel.ael',owner='asterisk')
		file_append('/etc/asterisk/extensions.ael','#include "zentinel.ael"')

def configure_tts():
	package_ensure('sox')
	package_ensure('mpg123')
	package_ensure('perl')
	package_ensure('libwww-perl')

	run('wget https://github.com/zaf/asterisk-googletts/archive/v0.6.tar.gz')
	run('tar xzvf v0.6.tar.gz')
	run('mv asterisk-googletts-0.6/googletts.agi /usr/share/asterisk/agi-bin')
	dir_remove('v0.6.tar.gz')

@task
def setup_system():
	addUsers()

@task
def configure_system():
	with mode_sudo():
		install_redis()
		package_update()
		package_ensure('vim')
		package_ensure('curl')
		package_ensure('asterisk')
		configure_asterisk()
		
# Application stuff
@task
def app_environment():
	# BROKEN
	# Don't work in Vagrant Windows 
	# with cd(PROJECT_ROOT):
		if not dir_exists('{0}/env/'.format(ENV_ROOT)):
			sudo('wget https://raw.github.com/pypa/virtualenv/1.9.X/virtualenv.py')
			sudo('python virtualenv.py {0}env/'.format(ENV_ROOT))
			sudo('env/bin/pip install -r {0}requirements.txt'.format(PROJECT_ROOT))

def python_requisites():
	with mode_sudo():
		# This should be in requisites.txt
		python_package_ensure_pip('redis')
		python_package_ensure_pip('hiredis')
		python_package_ensure_pip('rq')
		python_package_ensure_pip('Flask')

def prerequisites():
	package_ensure('python-dev')
	package_ensure('libevent-dev')
	python_requisites()

@task
def deploy():
	prerequisites()
	#app_environment()

@task
def provision():
	configure_system()
	deploy()
