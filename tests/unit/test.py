#!/usr/bin/python

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))[:-11]) # -6 gets rid of "/tests/unit"
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from tests.unit.suites.util import *
from tests.unit.suites.parsers.base import *
from tests.unit.suites.parsers.boolean import *
from tests.unit.suites.parsers.character import *
from tests.unit.suites.parsers.date import *
from tests.unit.suites.parsers.email import *
from tests.unit.suites.parsers.equation import *
from tests.unit.suites.parsers.measurement import *
from tests.unit.suites.parsers.name import *
from tests.unit.suites.parsers.number import *
from tests.unit.suites.parsers.phone import *
from tests.unit.suites.parsers.uri import *
