#!/usr/bin/python

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))[:-6])

from suites.parser import *
from suites.util import *
import unittest

if __name__ == '__main__':
    unittest.main()