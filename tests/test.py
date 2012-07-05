#!/usr/bin/python

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))[:-6])

from parser import *
import unittest


class BrainiacTestSuites:

    @staticmethod
    def parser():
        """Unit Tests for the Parser module"""
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


if __name__ == '__main__':
    unittest.TextTestRunner().run(BrainiacTestSuites.parser())
    