#!/usr/bin/python

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask import Flask, request
from mako.lookup import TemplateLookup
from cahoots import parser as CahootsParser
from web import out
import config

app = Flask(__name__,static_folder='web/static')

class CahootsWSGI(object):

    config = {}
    templateLookup = None
    
    def __init__(self, config):
        self.config = config
        self.configure_templating()

    def configure_templating(self):
        self.templateLookup = TemplateLookup(
            directories = self.config.template['lookups'],
            module_directory = self.config.template['modules']
        )
        
    def render(self, template, **context):
        rendered_template = self.templateLookup.get_template(template)
        return rendered_template.render(**context)

    def getRequestVariable(self, request, parameter):
        if request.method == 'POST':
            query = request.form.get(parameter, '')
        elif request.method == 'GET':
            query = request.args.get(parameter, '')

        return query


class CahootsClassifier(CahootsWSGI):
    
    def __init__(self, config):
        super(CahootsClassifier, self).__init__(config)
    
    def renderHome(self, request):
        query = self.getRequestVariable(request, 'q')
        
        results = None
        if query != '':
            results = CahootsParser.parse(query)
        
        return self.render('home.html', q = query, results = results, json_results = out.encode(results))


class CahootsClassifierApi(CahootsWSGI):

    def __init__(self, config):
        super(CahootsClassifierApi, self).__init__(config)
        
    def renderApi(self, request):
        query = self.getRequestVariable(request, 'q')
        
        results = None
        if query != '':
            results = CahootsParser.parse(query)
            
        return out.encode(results)


@app.route("/", methods=['POST', 'GET'])
def view_classifier():
    return CahootsClassifier(config).renderHome(request)


@app.route("/api/", methods=['POST', 'GET'])
def view_api():
    return CahootsClassifierApi(config).renderApi(request)


# This bootstraps our parsing system and gets all modules ready for parsing.
CahootsParser.bootstrap()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8000)), debug=True)
