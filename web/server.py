#!/usr/bin/python
"""
The MIT License (MIT)

Copyright (c) Serenity Software, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from flask import Flask, request
from mako.lookup import TemplateLookup
from cahoots.parser import CahootsParser
from web.config import WSGIConfig
from web import out
import os


APP = Flask(__name__, static_folder='static')

PARSER = CahootsParser(WSGIConfig, True)


class CahootsWSGI(object):
    """Handles all web/api responses"""

    parser = None
    template_lookup = None

    def __init__(self, cahoots_parser):
        self.parser = cahoots_parser
        self.configure_templating()

    def configure_templating(self):
        """sets up the template looker upper"""
        self.template_lookup = TemplateLookup(
            directories=self.parser.config.template['lookups'],
            module_directory=self.parser.config.template['modules']
        )

    def render(self, template, **context):
        """renders a provided template"""
        rendered_template = self.template_lookup.get_template(template)
        return rendered_template.render(**context)

    @classmethod
    def get_request_variable(cls, web_request, parameter):
        """retrieves a get or post request variable"""
        if web_request.method == 'POST':
            query = request.form.get(parameter, '')
        elif web_request.method == 'GET':
            query = request.args.get(parameter, '')

        return query


class CahootsClassifier(CahootsWSGI):
    """Responsible for handling web requests"""

    def __init__(self, cahoots_parser):
        super(CahootsClassifier, self).__init__(cahoots_parser)

    def render_home(self, web_request):
        """renders web interface"""
        query = self.get_request_variable(web_request, 'q')

        results = None
        if query != '':
            results = PARSER.parse(query)

        return self.render(
            'home.html',
            q=query,
            results=results,
            json_results=out.encode(results)
        )


class CahootsClassifierApi(CahootsWSGI):
    """Responsible for handling api requests"""

    def __init__(self, cahoots_parser):
        super(CahootsClassifierApi, self).__init__(cahoots_parser)

    def render_api(self, api_request):
        """renders cahoots response in json"""
        query = self.get_request_variable(api_request, 'q')

        results = None
        if query != '':
            results = PARSER.parse(query)

        return out.encode(results)


@APP.route("/", methods=['POST', 'GET'])
def view_classifier():
    """displays web interface"""
    return CahootsClassifier(PARSER).render_home(request)


@APP.route("/api/", methods=['POST', 'GET'])
def view_api():
    """displays a cahoots response in pure json"""
    return CahootsClassifierApi(PARSER).render_api(request)


if __name__ == "__main__":
    APP.run(
        host="0.0.0.0",
        port=int(os.environ.get('PORT', WSGIConfig.web_port)),
        debug=WSGIConfig.debug
    )
