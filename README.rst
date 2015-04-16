Cahoots
=======
A Text Comprehension Engine in Python
-------------------------------------

Build Status
------------
.. image:: https://travis-ci.org/SerenitySoftwareLLC/cahoots.svg?branch=master
.. image:: https://img.shields.io/badge/coverage-100%-brightgreen.svg?style=flat
.. image:: https://img.shields.io/badge/pylint-10.00/10-brightgreen.svg?style=flat
.. image:: https://img.shields.io/badge/flake8-passing-brightgreen.svg?style=flat

What is Cahoots?
----------------

Cahoots is software that attempts to categorize snippets of text into one of several categories. It runs a series of parsers, and returns a list of potential datatypes and interpretations with confidence values. In short, it attempts to "comprehend" the snippet you provide.

Its ideal use is within a daemon or service with a long life/execution time. It can also be run as a standalone Cahoots server (detailed `here <https://github.com/SerenitySoftwareLLC/cahoots/wiki/Cahoots-Server-Setup>`_).

What is Cahoots NOT?
--------------------

Cahoots is not meant for diagramming and mining large sets of text. While a text mining engine could utilize Cahoots in order to target specific snippets that it mined out of a large set of text, Cahoots is not meant to mine text.

Cahoots is not software that you would integrate into a non-daemon web app that would bootstrap and instantiate it on every page view. The bootstrap process can be somewhat intensive and should only run once (during an application's launch process).

Installation
------------
::

    sudo pip install cahoots

Basic Module Usage
------------------
.. code-block:: python

    >>> from cahoots.parser import CahootsParser
    >>> cahoots = CahootsParser(bootstrap=True)
    >>> results = cahoots.parse('http://www.google.com/')
    >>> results
    {
        'date': '2015-03-22T23:47:36.340187',
        'query': 'http://www.google.com/',
        'top': <cahoots.result.ParseResult object>,
        'results': {
            'count': 1,
            'matches': [
                <cahoots.result.ParseResult object>
            ],
            'types': [
                "URI"
            ]
        },
        'execution_seconds': 0.006306886672973633
    }

Basic Server Usage
------------------
.. code-block:: bash

    $ cahootserver --help

    Cahoots Server Help:

        -h, --help
            Show this help

        -p [port], --port [port]
            Set the port the server should listen on

        -d, --debug
            Run the server in debug mode (errors displayed, debug output)

    $ sudo cahootserver --port 80 --debug
     * 00:38:18 04/04/15 CDT * Bootstrapping AddressParser
     * 00:38:18 04/04/15 CDT * Bootstrapping CoordinateParser
     * 00:38:18 04/04/15 CDT * Bootstrapping DateParser
     * 00:38:18 04/04/15 CDT * Bootstrapping EmailParser
     * 00:38:18 04/04/15 CDT * Bootstrapping LandmarkParser
     * 00:38:18 04/04/15 CDT * Bootstrapping MeasurementParser
     * 00:53:19 04/05/15 CDT * Bootstrapping NameParser
     * 00:38:18 04/04/15 CDT * Bootstrapping PostalCodeParser
     * 00:38:18 04/04/15 CDT * Bootstrapping ProgrammingParser
     * Running on http://0.0.0.0:80/ (Press CTRL+C to quit)
     * Restarting with reloader
     * 00:38:18 04/04/15 CDT * Bootstrapping AddressParser
     * 00:38:18 04/04/15 CDT * Bootstrapping CoordinateParser
     * 00:38:18 04/04/15 CDT * Bootstrapping DateParser
     * 00:38:18 04/04/15 CDT * Bootstrapping EmailParser
     * 00:38:18 04/04/15 CDT * Bootstrapping LandmarkParser
     * 00:38:18 04/04/15 CDT * Bootstrapping MeasurementParser
     * 00:53:19 04/05/15 CDT * Bootstrapping NameParser
     * 00:38:18 04/04/15 CDT * Bootstrapping PostalCodeParser
     * 00:38:18 04/04/15 CDT * Bootstrapping ProgrammingParser
    # CTRL+C pressed

    $ sudo cahootserver --port 80
    $ ./cahootserver/server.py
     * Running on http://0.0.0.0:80/ (Press CTRL+C to quit)

Documentation
-------------
`What Is Cahoots? What Is Cahoots NOT? » <https://github.com/SerenitySoftwareLLC/cahoots/wiki>`_

`Requirements and Dependencies » <https://github.com/SerenitySoftwareLLC/cahoots/wiki/Requirements-and-Dependencies>`_

`Development Environment Setup » <https://github.com/SerenitySoftwareLLC/cahoots/wiki/Development-Environment-Setup>`_

`Cahoots Server Setup » <https://github.com/SerenitySoftwareLLC/cahoots/wiki/Cahoots-Server-Setup>`_

`Using Cahoots In Your Application » <https://github.com/SerenitySoftwareLLC/cahoots/wiki/Using-Cahoots-In-Your-Application>`_

`Demo of Cahoots Web Server » <http://cahoots.rwven.com/>`_

`API Documentation » <http://serenitysoftwarellc.github.io/cahoots/>`_

License
-------
::

    The MIT License (MIT)

    Copyright (c) 2012-2015 Serenity Software, LLC

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

Cahoots `integrates <https://github.com/SerenitySoftwareLLC/cahoots/blob/master/cahoots/parsers/location/data/LICENSE>`_ location data provided by `GeoNames <http://www.geonames.org/>`_.

Cahoots uses many code samples for training a bayesian classifier. All code samples are from projects using either the BSD or MIT `licenses <https://github.com/SerenitySoftwareLLC/cahoots/tree/master/cahoots/parsers/programming/LICENSES>`_. None of this code is executed at any time.
