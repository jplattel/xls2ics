from bottle import route, run, template, response, request, redirect, get, static_file
from bottle import jinja2_view

import functools
import os

# Configure to use jinja 2 templates
view = functools.partial(jinja2_view, template_lookup=['views'])

# Index
@route('/')
@view('index')
def index():
	return {}

@route('/<encoded_ics>')
@view('ics')
def view_ics(encoded_ics=False):
	return {'ics': encoded_ics}

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