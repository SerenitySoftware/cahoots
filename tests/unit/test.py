#!/usr/bin/python

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
import cahoots.parsers.grammar  # NOQA
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
from tests.unit.suites.parsers.grammar import *  # NOQA
from tests.unit.suites.parsers.location import *  # NOQA
from tests.unit.suites.parsers.measurement import *  # NOQA
from tests.unit.suites.parsers.name import *  # NOQA
from tests.unit.suites.parsers.number import *  # NOQA
from tests.unit.suites.parsers.phone import *  # NOQA
from tests.unit.suites.parsers.programming import ProgrammingParserTests  # NOQA
from tests.unit.suites.parsers.programming.bayesian import *  # NOQA
from tests.unit.suites.parsers.programming.lexer import *  # NOQA
from tests.unit.suites.parsers.uri import *  # NOQA
