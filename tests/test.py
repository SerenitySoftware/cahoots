#!/usr/bin/python

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))[:-6])

from suites.parser import *
from suites.util import *
import unittest


class BrainiacTestSuites:
    """Supplies the unit test suites"""

    @staticmethod
    def parser():
        """Unit tests for the parser module"""
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(NumberTests))
        suite.addTest(unittest.makeSuite(CharacterTests))
        suite.addTest(unittest.makeSuite(URITests))
        suite.addTest(unittest.makeSuite(EmailTests))
        suite.addTest(unittest.makeSuite(PhoneTests))
        suite.addTest(unittest.makeSuite(DateTester))
        suite.addTest(unittest.makeSuite(EquationTester))
        suite.addTest(unittest.makeSuite(ProgrammingTester))
        return suite

    @staticmethod
    def util():
        """Unit tests for the util module"""
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(BrainRegistryTests))
        suite.addTest(unittest.makeSuite(truncateTextTests))
        return suite


if __name__ == '__main__':
    print "Executing Test Suite: util"
    unittest.TextTestRunner().run(BrainiacTestSuites.util())

    print "Executing Test Suite: parser"
    unittest.TextTestRunner().run(BrainiacTestSuites.parser())
    