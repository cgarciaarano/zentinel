from flask import render_template,jsonify,make_response,abort,Response,request,session,redirect,flash,g
from zentinel.web import web, db, lm, oid
from zentinel.web.forms import LoginForm
from flask.ext.login import login_user, logout_user, current_user, login_required
from models import User
import StringIO
import mimetypes
import sys
import os
import pytz
from werkzeug.datastructures import Headers
from datetime import datetime,timedelta

import logging
import logging.handlers

# Login stuff
@lm.user_loader
def load_user(id):
	return User.query.get(int(id))


@oid.after_login
def after_login(resp):
	"""
	OpenID callback function
	"""
	if resp.email is None or resp.email == "":
		flash('Invalid login. Please try again.')
		return redirect(url_for('login'))
	user = User.query.filter_by(email = resp.email).first()
	if user is None:
		username = resp.nickname
		if username is None or username == "":
			username = resp.email.split('@')[0]
		user = User(username = username, email = resp.email)
		db.session.add(user)
		db.session.commit()
	remember_me = False
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))

@web.before_request
def before_request():
	g.user = current_user

# URLs
@web.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
	return render_template('login.html', 
		title = 'Sign In',
		form = form,
		providers = web.config['OPENID_PROVIDERS'])

@web.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@web.route('/')
@web.route('/index')
@login_required
def index():
	user = g.user

	return render_template('index.html',
		title = 'Home')


@web.errorhandler(500)
def error(error):
		return make_response(jsonify( { 'error': 'Server error' } ), 500)