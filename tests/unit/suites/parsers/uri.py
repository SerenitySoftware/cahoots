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

    def test_is_ipv6_address(self):
        self.assertTrue(self.up.is_ipv6_address("2607:f0d0:1002:51::4"))
        self.assertFalse(self.up.is_ipv6_address("2607:f0z0:1002:51::4"))
        self.assertFalse(self.up.is_ipv6_address("Your mother was a hamster"))

    def test_is_ipv4_address(self):
        self.assertTrue(self.up.is_ipv4_address("192.168.15.1"))
        self.assertTrue(self.up.is_ipv4_address("8.8.8.8"))
        self.assertFalse(self.up.is_ipv4_address("1.800.123.4567"))
        self.assertFalse(self.up.is_ipv4_address("Your mother was a hamster"))

    def test_is_valid_url(self):
        self.assertTrue(self.up.is_valid_url("http://www.google.com/"))
        self.assertFalse(self.up.is_valid_url("http://www.go_ogle.com/"))
        self.assertFalse(self.up.is_valid_url("www.google.com/"))
        self.assertFalse(self.up.is_valid_url("Your mother was a hamster"))

    def test_parseWithLessThanFourCharactersYieldsNothing(self):
        count = 0
        for result in self.up.parse('htt'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseIPV4AddressReturnsExpectedConfidence(self):
        count = 0
        for result in self.up.parse('192.168.0.1'):
            self.assertEqual(result.confidence, 95)
            self.assertEqual(result.subtype, 'IP Address (v4)')
            count += 1
        self.assertEqual(count, 1)

    def test_parseIPV6AddressReturnsExpectedConfidence(self):
        count = 0
        for result in self.up.parse('2607:f0d0:1002:51::4'):
            self.assertEqual(result.confidence, 100)
            self.assertEqual(result.subtype, 'IP Address (v6)')
            count += 1
        self.assertEqual(count, 1)

    def test_parseURLReturnsExpectedConfidence(self):
        count = 0
        for result in self.up.parse('http://www.google.com/'):
            self.assertEqual(result.confidence, 100)
            self.assertEqual(result.subtype, 'URL')
            count += 1
        self.assertEqual(count, 1)

    def test_parseNonHTTPURLReturnsExpectedConfidence(self):
        count = 0
        for result in self.up.parse('www.google.com/'):
            self.assertEqual(result.confidence, 75)
            self.assertEqual(result.subtype, 'URL')
            count += 1
        self.assertEqual(count, 1)
