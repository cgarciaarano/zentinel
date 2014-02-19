#!/usr/bin/env python
# encoding: utf-8

from fabric.api import *
from fabric.contrib.console import confirm
from cuisine import *
import os
import sys
from fabric.colors import red, green


def init_service():
	with mode_sudo():
		puts(green('Configuring circus init...'))
		config_template = text_strip_margin('''
		|start on (local-filesystems and net-device-up IFACE!=lo)
		|stop on shutdown
		|exec /usr/local/bin/circusd --log-output /var/log/circus/circus.log --log-level debug /etc/circus/circus.ini
		|respawn
		''')
		file_write('/etc/init/circus.conf', config_template)

def logrotate():
	with mode_sudo():
		puts(green('Configuring circus logrotate...'))
		exist = file_exists("/etc/logrotate.d/circus")
  		if not exist:
			sudo('touch /etc/logrotate.d/circus')
		config_template = text_strip_margin('''
		|/var/log/circus/*.log
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
		file_write('/etc/logrotate.d/circus', config_template)

def setup():
	with mode_sudo():
		puts(green('Configuring circus ...'))
		dir_ensure('/etc/circus', owner='root', group='root', mode="755")
		dir_ensure('/var/log/circus', owner='root', group='root', mode="755")
		dir_ensure('/var/log/chaussette', owner='root', group='root', mode="755")
		exist_log = file_exists("/var/log/circus/circus.log")
  		if not exist_log:
			sudo('touch /var/log/circus/circus.log')

def prerequisites():
	pass

def install():
	python_package_ensure_pip('circus')
	python_package_ensure_pip('circus-web')

def configure():
	init_service()
	logrotate()
	setup()

def deploy():
	prerequisites()
	install()
	configure()