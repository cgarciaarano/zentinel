from flask import render_template,jsonify,make_response,abort,Response,request,session,redirect
from app import app,db
from models import SMS
import xlwt
import StringIO
import mimetypes
import sys
import os
import pytz
from werkzeug.datastructures import Headers
from datetime import datetime,timedelta

import logging
import logging.handlers




@app.route('/', methods=['GET','POST'])
@app.route('/index/<int:page>', methods=['GET','POST'])
def index( page = 1 ):
	try:
		if 'sessionID' not in session:
			createSession()

		date_filters = setDateFilters()

		if request.method == 'POST':

			if request.form['date_filter'] is not None:
				session['date_filter'] = int(request.form['date_filter'])
			if request.form['timezone'] is not None:
				session['timezone'] = request.form['timezone']

		(from_date,to_date,label) = date_filters[session['date_filter']]

		smss = SMS.query.filter(SMS.creation_time.between(from_date,to_date)).order_by(SMS.creation_time.desc()).paginate(page, 20, False)	

		return render_template("index.html",\
			title = 'Home', smss = smss, selected = session['date_filter'], filters=enumerate(date_filters))
	except Exception as e:
		raise


@app.route("/export")
def export():
	if 'sessionID' not in session:
			return redirect(url_for('index'))

	response = Response()
	response.status_code = 200
	output = StringIO.StringIO()

	date_filters = setDateFilters()

	(from_date,to_date,label) = date_filters[session['date_filter']]

	smss = SMS.query.filter(SMS.creation_time.between(from_date,to_date)).order_by(SMS.creation_time.desc()).all()


	writeXLS(smss,output)
	
	response.data = output.getvalue()

	filename = 'sms.xls'
	mimetype_tuple = mimetypes.guess_type(filename)

	#HTTP headers for forcing file download
	response_headers = Headers({
					'Pragma': "public",  # required,
					'Expires': '0',
					'Cache-Control': 'must-revalidate, post-check=0, pre-check=0',
					'Cache-Control': 'private',  # required for certain browsers,
					'Content-Type': mimetype_tuple[0],
					'Content-Disposition': 'attachment; filename=\"%s\";' % filename,
					'Content-Transfer-Encoding': 'binary',
					'Content-Length': len(response.data)
			})

	if not mimetype_tuple[1] is None:
			response.update({
							'Content-Encoding': mimetype_tuple[1]
					})

	response.headers = response_headers

	return response


@app.route('/pin/<number>')
def createSMS(number):
	try:
		cc_number = '34' + number
		sms = SMS(cc_number)
		db.session.add(sms)
		sms.send()	
		db.session.commit()

		return jsonify( { 'pin':sms.getPin() } )

	except Exception as e:
		pass
		# I fuck it
		abort(500) 


@app.route('/dlr/<int:sms_id>/<int:dlr_code>')
def updateSMS(sms_id,dlr_code):
	try:
		sms = db.session.query(SMS).get(sms_id)
		sms.update(dlr_code)
		db.session.commit()

		return make_response(jsonify( {} ),200)

	except Exception as e:
		pass
		# I fuck it
		abort(500)		

@app.errorhandler(500)
def error(error):
		return make_response(jsonify( { 'error': 'Server error' } ), 500)	


def createSession():
	session['sessionID'] = os.urandom(24)
	session['date_filter'] = 0


def setDateFilters():
	filters = []
	
	now = datetime.utcnow()

	#if 'timezone' in session:
	#	tz = pytz.timezone(session['timezone'])
	#	now = pytz.utc.localize(now).astimezone(tz).replace(tzinfo=None) # Set to localtime

	# Last hour
	to_date = now
	from_date = to_date - timedelta(hours=1)
	filters.append((from_date,to_date,'Last hour'))

	# Last 3 hours
	to_date = now
	from_date = to_date - timedelta(hours=3)
	filters.append((from_date,to_date,'Last 3 hours'))

	# Today
	to_date = now
	from_date = to_date.date()
	filters.append((from_date,to_date,'Today'))

	# This week
	to_date = now
	from_date = datetime.fromordinal(to_date.date().toordinal() - now.weekday())
	filters.append((from_date,to_date,'This week'))

	# Previous week
	to_date = datetime.fromordinal(now.toordinal() - now.weekday())
	from_date = datetime.fromordinal(to_date.date().toordinal()-7)
	filters.append((from_date,to_date,'Previous week'))

	# This month
	to_date = now
	from_date = to_date.date().replace(day=1)
	filters.append((from_date,to_date,'This month'))
		
	# Previous month
	to_date = to_date.date().replace(day=1)
	from_date = (to_date - timedelta(days=1)).replace(day=1)
	filters.append((from_date,to_date,'Previous month'))

	# All
	to_date = now
	from_date = to_date.date().replace(year=1)
	filters.append((from_date,to_date,'All'))

	return filters

class FitSheetWrapper(object):
	"""Try to fit columns to max size of any entry.
	To use, wrap this around a worksheet returned from the 
	workbook's add_sheet method, like follows:

		sheet = FitSheetWrapper(book.add_sheet(sheet_name))

	The worksheet interface remains the same: this is a drop-in wrapper
	for auto-sizing columns.
	"""
	def __init__(self, sheet):
		self.sheet = sheet
		self.widths = dict()

	def write(self, r, c, label='', *args, **kwargs):
		self.sheet.write(r, c, label, *args, **kwargs)
		width = len(str(label))*300
		if width > self.widths.get(c, 0):
			self.widths[c] = width
			self.sheet.col(c).width = width

	def __getattr__(self, attr):
		return getattr(self.sheet, attr)

def writeXLS(data,output):
	"""
	Writes an XLS file. If it has more than 65000 rows, creates another sheet
		* data: List of objects
		* output: Contents of the XLS file
	"""

	if len(data) > 0:
		ezxf= xlwt.easyxf
		column_style = ezxf('font: name Calibri, height 220; border: left thin, right thin, top thin, bottom thin;')

		wbk = xlwt.Workbook(encoding='iso-8859-15')

		
		i = 0
		row_nr = 1
		# Adds new sheet, labeled with the name of the table and list with the fields
		sheet = addSheet(wbk,str(i),data[0].getXLSFields())
		for item in data: 
			for column_nr,column in enumerate(item.getXLSFields()):
				sheet.write(row_nr,column_nr,str(item.getXLSField(column)),column_style)

			row_nr += 1
			# If data has more than BATCH_LIMIT lines, flush the memory to avoid OOM
			if row_nr >1000:
				sheet.flush_row_data()

			# If data has more than EXCEL_LIMIT lines, a new sheet is needed
			if row_nr > 65000:
				i += 1
				row_nr = 1
				sheet = addSheet(wbk,str(i),data[0].getXLSFields())

		# Clean up memory
		sheet.flush_row_data()

		wbk.save(output)    

def addSheet(wbk,name,heading):
	"""
		Adds new sheet, with name provided and heading in form 
			 name: str
			 heading: list of fields [str]
	"""
	ezxf= xlwt.easyxf
	sheet = FitSheetWrapper(wbk.add_sheet(name))

	logger.debug('Writing headings for sheet {0}'.format(name))
	for column_nr,field in enumerate(heading):
		sheet.write(0,column_nr,field,ezxf('font: bold on, name Calibri, height 220; pattern: pattern solid, fore-colour 0x13; border: left thin, right thin, top thin, bottom thin;'))

	return sheet