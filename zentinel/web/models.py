from zentinel.web import db
from zentinel.core import logger
import hashlib
from datetime import datetime
from zentinel import settings
from sqlalchemy.dialects import postgresql


class Client(db.Model):
	id = db.Column(db.BigInteger, primary_key = True, unique=True,  autoincrement = True)
	name = db.Column(db.String(64), index = True)
	client_key = db.Column(db.String(254), unique = True, index = True)
	credits = db.Column(db.BigInteger)
	users = db.relationship('User', backref = 'client')
	numbers = db.relationship('DDI', backref = 'client')
	actions = db.relationship('ActionConfig', backref = 'client')
	active = db.Column(db.Boolean)

	def __init__(self):
		pass

	def __repr__(self):
		return '<Client {0}>'.format(self.name)

	def get_action(self, tag, step):
		"""
		Return the ActionConfig for the given params
		"""
		return ActionConfig.query.filter(ActionConfig.client_id == self.id, ActionConfig.tag == tag, ActionConfig.step == step).first()
		
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
	number = db.Column(db.BigInteger, primary_key = True, unique = True)
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
	__tablename__ = 'action_config'

	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	tag = db.Column(db.String(64), primary_key = True)
	step = db.Column(db.SmallInteger, primary_key = True)
	action_type = db.Column(db.String(128), nullable = False)	# Discriminator
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'))

	__mapper_args__ = {	'polymorphic_on': action_type,
						'with_polymorphic': '*'}

class Event(db.Model):
	__tablename__ = 'event'

	id = db.Column(db.BigInteger, primary_key = True, unique=True)
	message = db.Column(db.String(1024))
	tag = db.Column(db.String(64))
	step = db.Column(db.SmallInteger)
	ip_addr = db.Column(postgresql.INET)
	reception_date = db.Column(db.DateTime(timezone = True))
	execution_date = db.Column(db.DateTime(timezone = True))
	end_date = db.Column(db.DateTime(timezone = True))
	hash = db.Column(db.String(256), index = True)
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'))

	def __init__(self, client_id, ip_addr, message = '', tag = None, step = 1, reception_date = datetime.utcnow(), execution_date = None, end_date = None):
		self.client_id = client_id
		self.message = message
		self.tag = tag
		self.ip_addr = ip_addr
		self.reception_date = reception_date
		self.execution_date = execution_date
		self.end_date = end_date
		self.step = step
		self.hash = self.get_hash()


	@classmethod
	def from_dict(self,data):
		"""
		Creates an Event object from dict. Data must be sanitized!
		Used only when re-creating Event from EventQueue
		"""
		# FIXME Ugly workaround to avoid DB object
		attrs = ['client_id', 'message' ,'tag', 'ip_addr', 'reception_date', 'execution_date', 'end_date', 'step']

		dict_sane = True
		for attr in attrs:
			if attr not in data:
				dict_sane = False
				break

		if dict_sane:
			logger.debug("Event generated from dict: {0}".format(self))
			return Event(
				client_id = data['client_id'],\
				message = data['message'],\
				tag = data['tag'],\
				ip_addr = data['ip_addr'],\
				reception_date = data['reception_date'],\
				execution_date = data['execution_date'],\
				end_date = data['end_date'],\
				step = data['step'],\
				)

	def __str__(self):
		return str(self.__dict__)

	def get_data(self):
		# FIXME Ugly workaround to avoid DB object
		attrs = ['client_id', 'message' ,'tag', 'ip_addr', 'reception_date', 'execution_date', 'end_date', 'step']

		tmp_dict = {}
		for attr in attrs:
			tmp_dict[attr] = self.__dict__[attr]
		
		return tmp_dict

	def get_hash(self):
		# Get a uniqueid based in some attributes
		data = ''.join([str(self.client_id), self.message, self.tag, str(self.step)])
		return hashlib.sha256(str(data)).hexdigest()

	def save(self):
		# TODO Implement a real save
		print 'Event saved: {0}'.format(self)
# Actions Models
class SimpleCallParams(ActionConfig):
	__tablename__ = 'simple_call_params'

	id = db.Column(db.BigInteger, db.ForeignKey('action_config.id'), primary_key = True)
	ddi = db.Column(db.BigInteger, db.ForeignKey('DDI.number'))
	cli = db.Column(db.BigInteger)
	retries = db.Column(db.SmallInteger)

	__mapper_args__ = {'polymorphic_identity': 'SimpleCall',
						'inherit_condition': (id == ActionConfig.id)}

class AnnounceCallParams(ActionConfig):
	__tablename__ = 'announce_call_params'
	id = db.Column(db.BigInteger, db.ForeignKey('action_config.id'), primary_key = True)
	ddi = db.Column(db.BigInteger, db.ForeignKey('DDI.number'))
	cli = db.Column(db.Integer)
	retries = db.Column(db.SmallInteger)
	language = db.Column(db.Integer)
	__mapper_args__ = {	'polymorphic_identity': 'AnnouceCall',
						'inherit_condition': (id == ActionConfig.id)}

class AcknowledgedCallParams(ActionConfig):
	__tablename__ = 'acknowledged_call_params'

	id = db.Column(db.BigInteger, db.ForeignKey('action_config.id'), primary_key = True)
	ddi = db.Column(db.BigInteger, db.ForeignKey('DDI.number'))
	cli = db.Column(db.Integer)
	retries = db.Column(db.SmallInteger)
	language = db.Column(db.Integer)
	pin = db.Column(db.SmallInteger)

	__mapper_args__ = {'polymorphic_identity': 'AcknowledgedCall',
						'inherit_condition': (id == ActionConfig.id)}

class SimpleSMSParams(ActionConfig):
	__tablename__ = 'simple_sms_params'

	id = db.Column(db.BigInteger, db.ForeignKey('action_config.id'), primary_key = True)
	ddi = db.Column(db.BigInteger, db.ForeignKey('DDI.number'))
	cli = db.Column(db.Integer)
	retries = db.Column(db.SmallInteger)
	pin = db.Column(db.SmallInteger)

	__mapper_args__ = {'polymorphic_identity': 'SimpleSMS',
						'inherit_condition': (id == ActionConfig.id)}

class SimpleEmailParams(ActionConfig):
	__tablename__ = 'simple_email_params'

	id = db.Column(db.BigInteger, db.ForeignKey('action_config.id'), primary_key = True)
	email = db.Column(db.String(120), unique = True)
	retries = db.Column(db.SmallInteger)
	language = db.Column(db.Integer)
	pin = db.Column(db.SmallInteger)

	__mapper_args__ = {'polymorphic_identity': 'SimpleEmail',
					'inherit_condition': (id == ActionConfig.id)}	