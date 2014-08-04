from cahoots.parsers.email import EmailParser
from tests.unit.config import TestConfig
import unittest

class EmailParserTests(unittest.TestCase):
    """Unit Testing of the EmailParser"""

    ep = None

    def setUp(self):
        self.ep = EmailParser(TestConfig())

    def tearDown(self):
        self.ep = None

    def test_matchesEmailPattern(self):

        self.assertTrue(self.ep.matchesEmailPattern("jambra@photoflit.com"))
        self.assertTrue(self.ep.matchesEmailPattern("jambra+cahoots@photoflit.com"))
        self.assertTrue(self.ep.matchesEmailPattern("jambra.vennell@gmail.com"))
        self.assertTrue(self.ep.matchesEmailPattern("foo@photoflit.co.uk"))

        self.assertFalse(self.ep.matchesEmailPattern("asdf@asdf"))
        self.assertFalse(self.ep.matchesEmailPattern("asdfasdf"))
