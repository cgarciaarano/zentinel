from app import db
import hashlib
import datetime
import settings


class Client(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	credit
	user
	
class User(db.Model):
	__tablename__ = 'sms'
	__bind_key__ = 'db1'

	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	username = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)


    def __repr__(self):
        return '<User {0}>'.format(self.nickname)
		