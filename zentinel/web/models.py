from app import db
import hashlib
import datetime
import settings

class SMS(db.Model):
    __tablename__ = 'sms'
    __bind_key__ = 'db1'

    id = db.Column(db.BigInteger, primary_key = True, unique=True)
    number = db.Column(db.String(64), index = True)
    pin = db.Column(db.String(64), index = True)
    creation_time = db.Column(db.DateTime(timezone=True), index=True)
    sent = db.Column(db.Boolean)
    confirmed = db.Column(db.Boolean)
    dlr_code = db.Column(db.SmallInteger(),db.ForeignKey('dlr_code.code'))
    dlr_description = db.relationship("DLRCode")

    def __init__(self,number):      
        self.number = number
        self.creation_time = datetime.datetime.utcnow()
        self.sent = False
        self.confirmed = False
        self.dlr_code = None

        self.id = int(hashlib.sha1(self.number + str(self.creation_time)).hexdigest(),16)%10000000000
        self.pin = '{0:04d}'.format(self.id%10000)



    def __repr__(self):
        return '{0} \nNumber: {1} \nPIN:{2} \nSent: {3} \nConfirmed: {4} \nDLR code: {5}'.format(self.id,self.number,self.pin,self.sent,self.confirmed,self.dlr_code)

    def getPin(self):
        return self.pin

    def getKannelSMS(self):
        sms =   {   'momt':'MT',
                    'sender':'1234',
                    'receiver':self.number,
                    'msgdata':self.pin,
                    'sms_type':2,
                    'smsc_id':'silverstreet',
                    'boxc_id':'kannel',
                    'dlr_mask':31,
                    'meta_data':'?int?{0}'.format(self.id),
                    'dlr_url':'http://{0}:{1}/dlr/{2}/%d'.format(IPADDR,PORT,self.id)
                }

        return sms

    def send(self):
        try:        
            kannel_sms = KannelSMS(self.getKannelSMS())
            db.session.add(kannel_sms)
            db.session.commit()

            self.sent = True
        except Exception as e:
            raise

    def update(self,dlr_code):        
        self.dlr_code = dlr_code
        self.confirmed = True
        if dlr_code == 1:
            self.sent = True
        else:
            self.sent = False


    def getXLSFields(self):
        return self.__dict__.keys()

    def getXLSField(self,field):
        return self.__dict__[field]
        


class DLRCode(db.Model):
    __tablename__ = 'dlr_code'
    __bind_key__ = 'db1'

    code = db.Column(db.SmallInteger, primary_key = True)
    description = db.Column(db.String(256))



    def __repr__(self):
	return '{0} - {1}'.format(self.code,self.description)

class KannelSMS(db.Model):
    __bind_key__ = 'kannel'
    __table__ = db.Table('send_sms', db.Model.metadata,
        db.Column('id',db.BigInteger, primary_key = True, unique=True),
        db.Column('momt',db.Enum('MO','MT'), index = True),
        db.Column('sender',db.String, index = True),
        db.Column('receiver',db.String, index=True),
        db.Column('boxc_id',db.String(255)),
        db.Column('date',db.DateTime(timezone=True), index=True),
        db.Column('msgdata',db.Text),
        db.Column('sms_type',db.BigInteger),
        db.Column('smsc_id',db.String(255)),
        db.Column('dlr_mask',db.BigInteger),
        db.Column('dlr_url',db.String(255)),
        db.Column('meta_data',db.Text)
        )

    def __init__(self,dictionary):
        for key,value in dictionary.iteritems():
            setattr(self,key,value)