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
        self.assertTrue(self.ep.matchesEmailPattern("foobar@photoflit.com"))
        self.assertTrue(self.ep.matchesEmailPattern("foo+bar@photoflit.com"))
        self.assertTrue(self.ep.matchesEmailPattern("foo.bar@gmail.com"))
        self.assertTrue(self.ep.matchesEmailPattern("foo@photoflit.co.uk"))
        self.assertFalse(self.ep.matchesEmailPattern("asdf@asdf"))
        self.assertFalse(self.ep.matchesEmailPattern("asdfasdf"))

    def test_parseWithNoAtSymbolReturnsNothing(self):
        count = 0
        for result in self.ep.parse("Foo"):
            count += 1
        self.assertEqual(0, count)

    def test_parseDeterminesEmailValidityProperly(self):
        count = 0
        for result in self.ep.parse("foo@bar.com"):
            count += 1
            self.assertEqual("Email Address", result.Subtype)
            self.assertEqual(100, result.confidence)
        self.assertEqual(1, count)
