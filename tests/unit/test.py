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
# pylint: disable=unused-wildcard-import,wildcard-import,unused-import
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))[:-11])
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import cahoots  # NOQA
import cahoots.parser  # NOQA
import cahoots.config  # NOQA
import cahoots.parsers.base  # NOQA
import cahoots.parsers.boolean  # NOQA
import cahoots.parsers.character  # NOQA
import cahoots.parsers.date  # NOQA
import cahoots.parsers.email  # NOQA
import cahoots.parsers.equation  # NOQA
import cahoots.parsers.location  # NOQA
import cahoots.parsers.measurement  # NOQA
import cahoots.parsers.name  # NOQA
import cahoots.parsers.number  # NOQA
import cahoots.parsers.phone  # NOQA
import cahoots.parsers.programming  # NOQA
import cahoots.parsers.programming.bayesian  # NOQA
import cahoots.parsers.programming.lexer  # NOQA
import cahoots.parsers.uri  # NOQA
import cahoots.result  # NOQA
import cahoots.util  # NOQA

from tests.unit.suites.util import *  # NOQA
from tests.unit.suites.parser import *  # NOQA
from tests.unit.suites.parsers.base import *  # NOQA
from tests.unit.suites.parsers.boolean import *  # NOQA
from tests.unit.suites.parsers.character import *  # NOQA
from tests.unit.suites.parsers.date import *  # NOQA
from tests.unit.suites.parsers.email import *  # NOQA
from tests.unit.suites.parsers.equation import *  # NOQA
from tests.unit.suites.parsers.location import *  # NOQA
from tests.unit.suites.parsers.measurement import *  # NOQA
from tests.unit.suites.parsers.name import *  # NOQA
from tests.unit.suites.parsers.number import *  # NOQA
from tests.unit.suites.parsers.phone import *  # NOQA
from tests.unit.suites.parsers.programming import *  # NOQA
from tests.unit.suites.parsers.programming.bayesian import *  # NOQA
from tests.unit.suites.parsers.programming.lexer import *  # NOQA
from tests.unit.suites.parsers.uri import *  # NOQA
