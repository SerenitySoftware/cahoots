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
from cahoots.parsers import\
    boolean,\
    character,\
    date,\
    email,\
    equation,\
    measurement,\
    name,\
    number,\
    phone,\
    programming,\
    uri


class BaseConfig(object):
    """
    Cahoots Configuration
    Change this file to suit your installation's needs.
    """

    # Are we in debug mode?
    debug = False

    """
    To disable a module, simply comment it out of this list.
        Be aware that modules may have soft-dependencies on one another,
        and a disabled module may impact results results from other
        modules which seek its "council." This may result in unexpected
        confidence scores, a change in result determination, etc.
    """
    enabledModules = [
        name.NameParser,
        number.NumberParser,
        character.CharacterParser,
        boolean.BooleanParser,
        date.DateParser,
        phone.PhoneParser,
        uri.URIParser,
        email.EmailParser,
        programming.ProgrammingParser,
        # location.LocationParser,
        equation.EquationParser,
        measurement.MeasurementParser,
    ]

    """
    Redis config
        Specify one of the following three:
        1. host and port
         - Current values are the redis default
        2. unix_socket_path
         - The file path to the unix socket.
        3. connection_pool
          - Instance of redis.connection.ConnectionPool
    """
    redis = {
        'host': 'localhost',
        'port': 6379,
        'unix_socket_path': None,
        'connection_pool': None
    }

    """
    Configuration for the templating system
    """
    template = {
        'lookups': [
            'web/templates/'
        ],
        'modules': '/tmp/makocache/'
    }
