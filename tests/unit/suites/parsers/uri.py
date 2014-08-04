from cahoots.parsers.uri import URIParser
from tests.unit.config import TestConfig
import unittest

class URIParserTests(unittest.TestCase):
    """Unit Testing of the URIParser"""

    up = None

    def setUp(self):
        self.up = URIParser(TestConfig())

    def tearDown(self):
        self.up = None


    def test_isIPv6Address(self):

        self.assertTrue(self.up.isIPv6Address("2607:f0d0:1002:51::4"))

        self.assertFalse(self.up.isIPv6Address("2607:f0z0:1002:51::4"))
        self.assertFalse(self.up.isIPv6Address("Your mother was a hamster"))


    def test_isIPv4Address(self):

        self.assertTrue(self.up.isIPv4Address("192.168.15.1"))
        self.assertTrue(self.up.isIPv4Address("8.8.8.8"))

        self.assertFalse(self.up.isIPv4Address("1.800.123.4567"))
        self.assertFalse(self.up.isIPv4Address("Your mother was a hamster"))


    def test_isValidUrl(self):

        self.assertTrue(self.up.isValidUrl("http://www.google.com/"))

        self.assertFalse(self.up.isValidUrl("www.google.com/"))
        self.assertFalse(self.up.isValidUrl("Your mother was a hamster"))

