database = {
	'host': '127.0.0.1',
	'port': 27017,
	'database': 'brains'
}

template = {
	'lookups': ['/opt/brainiac/web/templates/'],
	'modules': '/tmp/makocache/'
}

from werkzeug.routing import Map, Rule

urls = Map([
	Rule('/', endpoint='home')
])