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

    def test_matches_email_pattern(self):
        self.assertTrue(self.ep.matches_email_pattern("foobar@photoflit.com"))
        self.assertTrue(self.ep.matches_email_pattern("foo+bar@photoflit.com"))
        self.assertTrue(self.ep.matches_email_pattern("foo.bar@gmail.com"))
        self.assertTrue(self.ep.matches_email_pattern("foo@photoflit.co.uk"))
        self.assertFalse(self.ep.matches_email_pattern("asdf@asdf"))
        self.assertFalse(self.ep.matches_email_pattern("asdfasdf"))

    def test_parseWithNoAtSymbolReturnsNothing(self):
        count = 0
        for result in self.ep.parse("Foo"):
            count += 1
        self.assertEqual(0, count)

    def test_parseDeterminesEmailValidityProperly(self):
        count = 0
        for result in self.ep.parse("foo@bar.com"):
            count += 1
            self.assertEqual("Email Address", result.subtype)
            self.assertEqual(100, result.confidence)
        self.assertEqual(1, count)
