#!/usr/bin/python

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))[:-6]) # -6 gets rid of "/tests"

from suites.parser import *
from suites.util import *
from suites.parsers.boolean import *
from suites.parsers.character import *
from suites.parsers.date import *
from suites.parsers.email import *
from suites.parsers.equation import *
from suites.parsers.name import *
import unittest

if __name__ == '__main__':
    unittest.main()