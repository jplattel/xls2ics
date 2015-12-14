from bottle import route, run, template, response, request, redirect, get, static_file
from bottle import jinja2_view

from datetime import timedelta
from icalendar import Calendar, Event

import functools
import os
import datetime

# Configure to use jinja 2 templates
view = functools.partial(jinja2_view, template_lookup=['views'])


# Magic: http://stackoverflow.com/questions/1108428/how-do-i-read-a-date-in-excel-format-in-python
def xldate_as_datetime(xldate, datemode):
    if datemode not in (0, 1):
        raise XLDateBadDatemode(datemode)
    if xldate == 0.00:
        return datetime.time(0, 0, 0)
    if xldate < 0.00:
        raise XLDateNegative(xldate)
    xldays = int(xldate)
    frac = xldate - xldays
    seconds = int(round(frac * 86400.0))
    assert 0 <= seconds <= 86400
    if seconds == 86400:
        seconds = 0
        xldays += 1
    #if xldays >= _XLDAYS_TOO_LARGE[datemode]:
    #    raise XLDateTooLarge(xldate)

    if xldays == 0:
        # second = seconds % 60; minutes = seconds // 60
        minutes, second = divmod(seconds, 60)
        # minute = minutes % 60; hour    = minutes // 60
        hour, minute = divmod(minutes, 60)
        return datetime.time(hour, minute, second)

    if xldays < 61 and datemode == 0:
        raise XLDateAmbiguous(xldate)

    return (
        datetime.datetime.fromordinal(xldays + 693594 + 1462 * datemode)
        + datetime.timedelta(seconds=seconds)
        )

def xlminutes_to_normal_minutes(xlminute):
	normal_minutes = xlminute * 60 * 24
	return timedelta(minutes=normal_minutes)


def parse_excel_string():
	pass

# Index
@route('/')
@view('index')
def index():
	return {}


@route('/ics/<encoded_ics>')
def download_ics(encoded_ics=False):

	cal = Calendar()

	# Parse get request
	events = encoded_ics.split('|')

	for e in events:

		e = e.split(';')

		event = Event()
		if len(e) is 2:
			description = e[0]
			dag = xldate_as_datetime(int(e[1]), 0)
			starttijd = dag + timedelta(minutes=720)
			eindetijd = starttijd + timedelta(minutes=15)
			event.add('summary', description)
			event.add('dtstart', starttijd)
			event.add('dtend', eindetijd)
			cal.add_component(event)

		elif len(e) is 4:
			description = e[0]
			dag = xldate_as_datetime(int(e[1]), 0)
			starttijd = dag + xlminutes_to_normal_minutes(float(e[2].replace(',','.')))
			eindetijd = starttijd + xlminutes_to_normal_minutes(float(e[3].replace(',','.')))
			event.add('summary', description)
			event.add('dtstart', starttijd)
			event.add('dtend', eindetijd)
			cal.add_component(event)

	response.set_header('Content-Type', 'text/calendar')
	response.set_header("Content-Disposition", "attachment; filename=afspraken.ics");

	ics = cal.to_ical()
	return ics


@route('/<encoded_ics>')
@view('ics')
def view_ics(encoded_ics=False):

	data = []	
	events = encoded_ics.split('|')
	for e in events:
		e = e.split(';')

		event = Event()
		if len(e) is 2:
			description = e[0]
			dag = xldate_as_datetime(int(e[1]), 0)
			starttijd = dag + timedelta(minutes=720)
			eindetijd = starttijd + timedelta(minutes=15)
			data.append({'summary': description, 'dtstart': starttijd, 'dtend': eindetijd, 'dag': e[1], 'ics_start': '0.5', 'ics_eind':'0.01041666666667'})

		elif len(e) is 4:
			description = e[0]
			dag = xldate_as_datetime(int(e[1]), 0)
			starttijd = dag + xlminutes_to_normal_minutes(float(e[2].replace(',','.')))
			eindetijd = starttijd + xlminutes_to_normal_minutes(float(e[3].replace(',','.')))
			data.append({'summary': description, 'dtstart': starttijd, 'dtend': eindetijd, 'dag': e[1], 'ics_start': e[2], 'ics_eind': e[3]})			

	return {'data': data, 'encoded_ics': encoded_ics}


# Static Routes
@get('/static/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='static/js')

@get('/static/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='static/css')

@get('/static/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='static/img')

@get('/static/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
    return static_file(filename, root='static/fonts')

if __name__ == '__main__':
	run(host='0.0.0.0', port=os.environ.get('PORT', 8888))