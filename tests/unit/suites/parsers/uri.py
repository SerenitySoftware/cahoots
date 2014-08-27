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
        self.assertFalse(self.up.isValidUrl("http://www.go_ogle.com/"))
        self.assertFalse(self.up.isValidUrl("www.google.com/"))
        self.assertFalse(self.up.isValidUrl("Your mother was a hamster"))

    def test_parseWithLessThanFourCharacters(self):
        count = 0
        for result in self.up.parse('htt'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseIPV4AddressReturnsExpectedConfidence(self):
        count = 0
        for result in self.up.parse('192.168.0.1'):
            self.assertEqual(result.Confidence, 95)
            self.assertEqual(result.Subtype, 'IP Address (v4)')
            count += 1
        self.assertEqual(count, 1)

    def test_parseIPV6AddressReturnsExpectedConfidence(self):
        count = 0
        for result in self.up.parse('2607:f0d0:1002:51::4'):
            self.assertEqual(result.Confidence, 100)
            self.assertEqual(result.Subtype, 'IP Address (v6)')
            count += 1
        self.assertEqual(count, 1)

    def test_parseURLReturnsExpectedConfidence(self):
        count = 0
        for result in self.up.parse('http://www.google.com/'):
            self.assertEqual(result.Confidence, 100)
            self.assertEqual(result.Subtype, 'URL')
            count += 1
        self.assertEqual(count, 1)

    def test_parseNonHTTPURLReturnsExpectedConfidence(self):
        count = 0
        for result in self.up.parse('www.google.com/'):
            self.assertEqual(result.Confidence, 75)
            self.assertEqual(result.Subtype, 'URL')
            count += 1
        self.assertEqual(count, 1)
