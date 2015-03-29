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
from cahootserver.config import WSGIConfig
from cahootserver import out
import os
import sys
import getopt


APP = Flask(
    __name__,
    static_folder=os.path.dirname(os.path.realpath(__file__)) + '/static'
)

# Will instantiate this later
PARSER = CahootsParser


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


class CahootsClassifier(CahootsWSGI):
    """Responsible for handling web requests"""

    def __init__(self, cahoots_parser):
        super(CahootsClassifier, self).__init__(cahoots_parser)

    def render_home(self, web_request):
        """renders web interface"""
        query = web_request.form.get('snippet', '')

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

    @classmethod
    def render_api(cls, api_request):
        """renders cahoots response in json"""
        query = api_request.form.get('snippet', '')

        results = None
        if query != '':
            results = PARSER.parse(query)

        return out.encode(results)


@APP.route("/", methods=['POST', 'GET'])
def view_classifier():
    """displays web interface"""
    return CahootsClassifier(PARSER).render_home(request)


@APP.route("/api/", methods=['POST'])
@APP.route("/api", methods=['POST'])
def view_api():
    """displays a cahoots response in pure json"""
    return CahootsClassifierApi(PARSER).render_api(request)


def usage():
    """Cahoots Help"""
    print("")
    print("Cahoots Server Help:")
    print("")
    print("\t-h, --help")
    print("\t\tShow this help")
    print("")
    print("\t-p [port], --port [port]")
    print("\t\tSet the port the server should listen on")
    print("")
    print("\t-d, --debug")
    print("\t\tRun the server in debug mode (errors displayed, debug output)")
    print("")


def launch_server():
    """
    Runs our server!
    """
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:],
            "hp:d",
            ["help", "port=", "debug"]
        )
    except getopt.GetoptError as gerror:
        print('\nError: ' + gerror.msg)
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            WSGIConfig.debug = True
        elif opt in ("-p", "--port"):
            try:
                WSGIConfig.web_port = int(arg)
                if WSGIConfig.web_port > 65535:
                    raise ValueError
            except ValueError:
                print('\nError: Invalid port')
                usage()
                sys.exit()

    # pylint: disable=global-statement
    global PARSER
    PARSER = CahootsParser(WSGIConfig, True)

    APP.run(
        host="0.0.0.0",
        port=int(os.environ.get('PORT', WSGIConfig.web_port)),
        debug=WSGIConfig.debug
    )


if __name__ == "__main__":
    launch_server()
