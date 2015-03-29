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

import cahoots  # flake8: noqa
import cahoots.confidence.normalizer  # flake8: noqa
import cahoots.confidence.normalizers.base  # flake8: noqa
import cahoots.confidence.normalizers.character  # flake8: noqa
import cahoots.confidence.normalizers.date  # flake8: noqa
import cahoots.confidence.normalizers.equation  # flake8: noqa
import cahoots.confidence.normalizers.number  # flake8: noqa
import cahoots.confidence.normalizers.phone  # flake8: noqa
import cahoots.config  # flake8: noqa
import cahoots.parsers.base  # flake8: noqa
import cahoots.parsers.boolean  # flake8: noqa
import cahoots.parsers.character  # flake8: noqa
import cahoots.parsers.date  # flake8: noqa
import cahoots.parsers.email  # flake8: noqa
import cahoots.parsers.equation  # flake8: noqa
import cahoots.parsers.location  # flake8: noqa
import cahoots.parsers.location.address  # flake8: noqa
import cahoots.parsers.location.coordinate  # flake8: noqa
import cahoots.parsers.location.landmark  # flake8: noqa
import cahoots.parsers.location.postalcode  # flake8: noqa
import cahoots.parsers.measurement  # flake8: noqa
import cahoots.parsers.name  # flake8: noqa
import cahoots.parsers.number  # flake8: noqa
import cahoots.parsers.phone  # flake8: noqa
import cahoots.parsers.programming  # flake8: noqa
import cahoots.parsers.programming.bayesian  # flake8: noqa
import cahoots.parsers.programming.lexer  # flake8: noqa
import cahoots.parsers.uri  # flake8: noqa
import cahoots.data  # flake8: noqa
import cahoots.parser  # flake8: noqa
import cahoots.result  # flake8: noqa
import cahoots.util  # flake8: noqa

from tests.confidence.normalizer import *  # flake8: noqa
from tests.confidence.normalizers.base import *  # flake8: noqa
from tests.confidence.normalizers.character import *  # flake8: noqa
from tests.confidence.normalizers.date import *  # flake8: noqa
from tests.confidence.normalizers.equation import *  # flake8: noqa
from tests.confidence.normalizers.number import *  # flake8: noqa
from tests.confidence.normalizers.phone import *  # flake8: noqa
from tests.parsers.base import *  # flake8: noqa
from tests.parsers.boolean import *  # flake8: noqa
from tests.parsers.character import *  # flake8: noqa
from tests.parsers.date import *  # flake8: noqa
from tests.parsers.email import *  # flake8: noqa
from tests.parsers.equation import *  # flake8: noqa
from tests.parsers.location import *  # flake8: noqa
from tests.parsers.location.address import *  # flake8: noqa
from tests.parsers.location.coordinate import *  # flake8: noqa
from tests.parsers.location.landmark import *  # flake8: noqa
from tests.parsers.location.postalcode import *  # flake8: noqa
from tests.parsers.measurement import *  # flake8: noqa
from tests.parsers.name import *  # flake8: noqa
from tests.parsers.number import *  # flake8: noqa
from tests.parsers.phone import *  # flake8: noqa
from tests.parsers.programming import *  # flake8: noqa
from tests.parsers.programming.bayesian import *  # flake8: noqa
from tests.parsers.programming.lexer import *  # flake8: noqa
from tests.parsers.uri import *  # flake8: noqa
from tests.data import *  # flake8: noqa
from tests.parser import *  # flake8: noqa
from tests.util import *  # flake8: noqa
