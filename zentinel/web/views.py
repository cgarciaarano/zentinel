from flask import render_template,jsonify,make_response,abort,Response,request,session,redirect,flash
from zentinel.web import web
from zentinel.web.forms import LoginForm
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


@web.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = web.config['OPENID_PROVIDERS'])

@web.errorhandler(500)
def error(error):
		return make_response(jsonify( { 'error': 'Server error' } ), 500)	


def createSession():
	session['sessionID'] = os.urandom(24)
	session['date_filter'] = 0


