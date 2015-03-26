Cahoots
=======
A Text Comprehension Engine in Python
-------------------------------------

Build Status
------------
[![Build Status](https://travis-ci.org/SerenitySoftwareLLC/cahoots.svg?branch=master)](https://travis-ci.org/SerenitySoftwareLLC/cahoots)
[![Build Status](https://img.shields.io/badge/coverage-100%-brightgreen.svg?style=flat)](https://travis-ci.org/SerenitySoftwareLLC/cahoots)
[![Build Status](https://img.shields.io/badge/pylint-10.00/10-brightgreen.svg?style=flat)](https://travis-ci.org/SerenitySoftwareLLC/cahoots)
[![Build Status](https://img.shields.io/badge/flake8-passing-brightgreen.svg?style=flat)](https://travis-ci.org/SerenitySoftwareLLC/cahoots)

What is Cahoots?
----------------

Cahoots is software that attempts to categorize snippets of text into one of several categories. It runs a series of parsers, and returns a list of potential datatypes and interpretations with confidence values. In short, it attempts to "comprehend" the snippet you provide.

Its ideal use is within a daemon or service with a long life/execution time. It can also be run as a standalone Cahoots server (detailed [here](https://github.com/SerenitySoftwareLLC/cahoots/wiki/Cahoots-Server-Setup)).

What is Cahoots NOT?
--------------------

Cahoots is not meant for diagramming and mining large sets of text. While a text mining engine could utilize Cahoots in order to target specific snippets that it mined out of a large set of text, Cahoots is not meant to mine text.

Cahoots is not software that you would integrate into a non-daemon web app that would bootstrap and instantiate it on every page view. The bootstrap process can be somewhat intensive and should only run once (during an application's launch process).

Installation
------------
```bash
sudo pip install cahoots
```

Basic Module Usage
------------------
```python
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
```

Basic Server Usage
------------------
```bash
$ cahootserver --help

Cahoots Server Help:

    -h, --help
        Show this help

    -p [port], --port [port]
        Set the port the server should listen on

    -d, --debug
        Run the server in debug mode (errors displayed, debug output)

$ sudo cahootserver --port 80 --debug
 * 21:52:30 03/25/15 CDT * Bootstrapping AddressParser
 * 21:52:30 03/25/15 CDT * Bootstrapping CoordinateParser
 * 21:52:30 03/25/15 CDT * Bootstrapping EmailParser
 * 21:52:30 03/25/15 CDT * Bootstrapping LandmarkParser
 * 21:52:30 03/25/15 CDT * Bootstrapping MeasurementParser
 * 21:52:30 03/25/15 CDT * Bootstrapping PostalCodeParser
 * 21:52:30 03/25/15 CDT * Bootstrapping ProgrammingParser
 * Running on http://0.0.0.0:80/ (Press CTRL+C to quit)
 * Restarting with reloader
 * 21:52:34 03/25/15 CDT * Bootstrapping AddressParser
 * 21:52:34 03/25/15 CDT * Bootstrapping CoordinateParser
 * 21:52:34 03/25/15 CDT * Bootstrapping EmailParser
 * 21:52:34 03/25/15 CDT * Bootstrapping LandmarkParser
 * 21:52:34 03/25/15 CDT * Bootstrapping MeasurementParser
 * 21:52:34 03/25/15 CDT * Bootstrapping PostalCodeParser
 * 21:52:34 03/25/15 CDT * Bootstrapping ProgrammingParser
# CTRL+C pressed

$ sudo cahootserver --port 80
$ ./cahootserver/server.py
 * Running on http://0.0.0.0:80/ (Press CTRL+C to quit)
```

Documentation
-------------

#### [What Is Cahoots? What Is Cahoots NOT? »](https://github.com/SerenitySoftwareLLC/cahoots/wiki)

#### [Requirements and Dependencies »](https://github.com/SerenitySoftwareLLC/cahoots/wiki/Requirements-and-Dependencies)

#### [Development Environment Setup »](https://github.com/SerenitySoftwareLLC/cahoots/wiki/Development-Environment-Setup)

#### [Cahoots Server Setup »](https://github.com/SerenitySoftwareLLC/cahoots/wiki/Cahoots-Server-Setup)

#### [Using Cahoots In Your Application »](https://github.com/SerenitySoftwareLLC/cahoots/wiki/Using-Cahoots-In-Your-Application)

#### [Demo of Cahoots Web Server »](http://cahoots.rwven.com/)

License
-------
```
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
```

Cahoots [integrates](https://github.com/hickeroar/cahoots/blob/master/cahoots/parsers/location/data/LICENSE) location data provided by [GeoNames](http://www.geonames.org/).

Cahoots uses many code samples for training a bayesian classifier. All code samples are from projects using either the BSD or MIT [licenses](https://github.com/hickeroar/cahoots/tree/master/cahoots/parsers/programming/LICENSES). None of this code is executed at any time.
