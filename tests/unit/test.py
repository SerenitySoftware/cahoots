#!/usr/bin/python

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))[:-11])
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from tests.unit.suites.util import *  # NOQA
from tests.unit.suites.parsers.base import *  # NOQA
from tests.unit.suites.parsers.boolean import *  # NOQA
from tests.unit.suites.parsers.character import *  # NOQA
from tests.unit.suites.parsers.date import *  # NOQA
from tests.unit.suites.parsers.email import *  # NOQA
from tests.unit.suites.parsers.equation import *  # NOQA
from tests.unit.suites.parsers.measurement import *  # NOQA
from tests.unit.suites.parsers.name import *  # NOQA
from tests.unit.suites.parsers.number import *  # NOQA
from tests.unit.suites.parsers.phone import *  # NOQA
from tests.unit.suites.parsers.uri import *  # NOQA
