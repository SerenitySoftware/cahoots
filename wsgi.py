#!/usr/bin/python

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask import Flask, request, redirect
from mako.lookup import TemplateLookup
from brain import parser
from web import out
import config

app = Flask(__name__,static_folder='web/static')


class BrainiacWSGI(object):

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


class BrainiacClassifier(BrainiacWSGI):
    
    def __init__(self, config):
        super(BrainiacClassifier, self).__init__(config)
    
    def renderHome(self, request):
        query = self.getRequestVariable(request, 'q')
        
        results = None
        if query != '':
            results = parser.parse(query)
        
        return self.render('home.html', q = query, results = results, json_results = out.encode(results))


class BrainiacClassifierApi(BrainiacWSGI):

    def __init__(self, config):
        super(BrainiacClassifierApi, self).__init__(config)
        
    def renderApi(self, request):
        query = self.getRequestVariable(request, 'q')
        
        results = None
        if query != '':
            results = parser.parse(query)
            
        return out.encode(results)


@app.route("/")
def classifierRedirect():
    return redirect("/classifier/")


@app.route("/classifier/", methods=['POST', 'GET'])
def classifier():
    classifier = BrainiacClassifier(config)
    return classifier.renderHome(request)


@app.route("/classifier/api/", methods=['POST', 'GET'])
def classifierApi():
    classifier = BrainiacClassifierApi(config)
    return classifier.renderApi(request)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8000), debug=True)
