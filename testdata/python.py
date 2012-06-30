import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import pymongo
import urlparse
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.serving import run_simple
from werkzeug.utils import redirect
from mako import *
from mako.template import Template
from mako.lookup import TemplateLookup
import config
from brain import parser
from web import out



class BrainiacWSGI(object):

    config = {}
    
    def __init__(self, config):
        self.config = config
        
        self.configure_database()
        self.configure_templating()
        self.configure_routing()
        
    def configure_database(self):
        pass
        #self.db = pymongo.Connection(self.config.database['host'], self.config.database['port'])[self.config.database['database']]
        
    def configure_templating(self):
        self.template_lookup = TemplateLookup(
            directories = self.config.template['lookups'],
            module_directory = self.config.template['modules']
        )
        
    def configure_routing(self):
        self.urls = self.config.urls
        
    def render(self, template, **context):
        rendered_template = self.template_lookup.get_template(template)
        return Response(rendered_template.render(**context), mimetype='text/html')
        
    def dispatch_request(self, request):
        adapter = self.urls.bind_to_environ(request.environ)
        
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'view_' + endpoint)(request, **values)
        except HTTPException, e:
            return e
            
    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)
        
        
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

class BrainiacWeb(BrainiacWSGI):
    
    def __init__(self, config):
        super(BrainiacWeb, self).__init__(config)
        
    def view_home(self, request):
        query = request.form.get('q', '')
        
        results = None
        if query != '':
            results = parser.parse(query)
        
        return self.render('home.html', q = query, results = results, json_results = out.encode(results))
        
class BrainiacAPI(BrainiacWSGI):

    def __init__(self, config):
        super(BrainiacAPI, self).__init__(config)
        
    def view_home(self, request):
        query = request.form.get('q', '')
        
        results = None
        if query != '':
            results = parser.parse(query)
            
        return Response(out.encode(results), mimetype='text/html')
        
def wsgi_start(ip, port, app_type, use_debugger = True, use_reloader = True):
    app = app_type(config)
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/static':  os.path.join(os.path.dirname(__file__), 'web/static')
    })
    
    run_simple(ip, port, app, use_debugger, use_reloader)
    
if __name__ == '__main__':
    wsgi_start('0.0.0.0', 8000, BrainiacWeb)
    #wsgi_start('0.0.0.0', 8080, BrainiacAPI)