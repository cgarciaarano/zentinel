from zentinel.web import db
import hashlib
from datetime import datetime
import settings


class Client(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	name = db.Column(db.String(64), index = True)
	client_key = db.Column(db.String(254), primary_key = True, unique = True)
	credits = db.Column(db.BigInteger)
	users = db.relationship('User', backref = 'user')

	def __init__(self):
		pass
	def __repr__(self):
		return '<Client {0}>'.format(self.name)
		
class User(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	username = db.Column(db.String(64), index = True, unique = True)
	email = db.Column(db.String(120), unique = True)
	last_login = db.Column(db.DateTime(timezone = True))
	creation_date = db.Column(db.DateTime(timezone = True))
	last_modification = db.Column(db.DateTime(timezone = True))
	password = db.Column(db.String(128))
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
	
	def __init__(self, username, email, password):
		self.username = username
		self.email = email
		self.password = password
		self.creation_date = datetime.utcnow()
		self.last_modification = datetime.utcnow()

	def __repr__(self):
		return '<User {0}>'.format(self.username)
		
class ActionConfig(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	tag = db.Column(db.String(64), primary_key = True)
	step = db.Column(db.SmallInteger, primary_key = True)
	action_type = db.Column(db.String(128))