from zentinel.web import db
import hashlib
from datetime import datetime
import settings


class Client(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True,  autoincrement = True)
	name = db.Column(db.String(64), index = True)
	client_key = db.Column(db.String(254), primary_key = True, unique = True)
	credits = db.Column(db.BigInteger)
	users = db.relationship('User', backref = 'client')
	numbers = db.relationship('DDI', backref = 'client')
	actions = db.relationship('ActionConfig', backref = 'client')
	active = db.Column(db.Boolean)

	def __init__(self):
		pass
	def __repr__(self):
		return '<Client {0}>'.format(self.name)
		
class User(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique = True, autoincrement = True)
	username = db.Column(db.String(64), index = True, unique = True)
	email = db.Column(db.String(120), unique = True)
	last_login = db.Column(db.DateTime(timezone = True))
	creation_date = db.Column(db.DateTime(timezone = True), default = datetime.utcnow)
	last_modification = db.Column(db.DateTime(timezone = True), onupdate = datetime.utcnow)
	#password = db.Column(db.String(128))
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
	active = db.Column(db.Boolean)

	def is_authenticated(self):
		return True

	def is_active(self):
		return self.active

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def __repr__(self):
		return '<User {0}>'.format(self.username)
		
class DDI(db.Model):
	number = db.Column(db.Integer, primary_key = True, unique = True)
	country_code = db.Column(db.Integer, db.ForeignKey('country.code'))
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
	creation_date = db.Column(db.DateTime(timezone = True), default = datetime.utcnow)
	active = db.Column(db.Boolean)

class Country(db.Model):
	code = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(128))
	iso_name = db.Column(db.String(5))
	numbers = db.relationship('DDI', backref = 'country')

class ActionConfig(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	tag = db.Column(db.String(64), primary_key = True)
	step = db.Column(db.SmallInteger, primary_key = True)
	action_type = db.Column(db.String(128)) # Sould be an enum or a Foreing Key
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'))