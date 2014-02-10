#!/usr/bin/env python
# encoding: utf-8

from fabric.api import *
from fabric.contrib.console import confirm
from cuisine import *
import os
import sys
from fabric.colors import red, green
import circus, redis, asterisk

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

def custom_asterisk():
	with mode_sudo():
		configure_tts()

		file_link(PROJECT_ROOT + 'core/actions/zentinel.ael','/etc/asterisk/zentinel.ael',owner='asterisk')
		file_append('/etc/asterisk/extensions.ael','#include "zentinel.ael"')

def custom_circus():
	with mode_sudo():
		file_link(PROJECT_ROOT + 'fabfile/circus/circus.ini','/etc/circus/circus.ini',owner='root')
		dir_ensure('/var/log/zentinel')

def logs():
	with mode_sudo():
		puts(green('Configuring zentinel logs...'))
		config_template = text_strip_margin('''
		|local0.*        /var/log/zentinel/web.log
		|local1.*        /var/log/zentinel/core.log
		''')
		file_write('/etc/rsyslog.d/zentinel.conf', config_template)

def logrotate():
	with mode_sudo():
		exist = file_exists("/etc/logrotate.d/zentinel")
	  	if not exist:
			run('touch /etc/logrotate.d/circus')
		config_template = text_strip_margin('''
		|/var/log/zentinel/*.log
		|{
		|        rotate 7
		|        daily
		|        missingok
		|        size 500M
		|        notifempty
		|        copytruncate
		|        delaycompress
		|        compress
		|}
		''')
		file_write('/etc/logrotate.d/zentinel', config_template)

def configure_tts():
	package_ensure('sox')
	package_ensure('mpg123')
	package_ensure('perl')
	package_ensure('libwww-perl')

	run('wget https://github.com/zaf/asterisk-googletts/archive/v0.6.tar.gz')
	run('tar xzvf v0.6.tar.gz')
	run('mv asterisk-googletts-0.6/googletts.agi /usr/share/asterisk/agi-bin')
	dir_remove('v0.6.tar.gz')


def configure_web():
	python_package_ensure_pip('chaussette')
	package_ensure('libev-dev')
	python_package_ensure_pip('bjoern')

@task
def setup_system():
	addUsers()

@task
def configure_system():
	with mode_sudo():
		package_update()
		package_ensure('vim')
		package_ensure('curl')
		
		redis.deploy()
		asterisk.deploy()
		circus.deploy()
		
		custom_asterisk()
		custom_circus()

		configure_web()
		logs()
		logrotate()
		
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
		python_package_ensure_pip('Flask-Cache')

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
