from zentinel.web import db
import hashlib
import datetime
import settings


class Client(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	name = db.Column(db.String(64))
	client_key = db.Column(db.String(254), primary_key = True, unique = True)
	credits = db.Column(db.BigInteger)

	
class User(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	username = db.Column(db.String(64), index = True, unique = True)
	email = db.Column(db.String(120), index = True, unique = True)
	last_login = db.Column(db.DateTime(timezone = True))
	creation_date = db.Column(db.DateTime(timezone = True))
	last_modification = db.Column(db.DateTime(timezone = True))
	password = db.Column(db.String(128))
	#pedo = db.Column(db.String(128))



	def __repr__(self):
		return '<User {0}>'.format(self.nickname)
		
class ActionConfig(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	tag = db.Column(db.String(64), primary_key = True, index = True, unique = True)
	step = db.Column(db.SmallInteger, primary_key = True, index = True, unique = True)
	action_type = db.Column(db.String(128))