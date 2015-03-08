from cahoots.parsers.date import DateParser
from tests.unit.config import TestConfig
import unittest


class DateParserTests(unittest.TestCase):
    """Unit Testing of the DateParser"""

    dp = None

    def setUp(self):
        self.dp = DateParser(TestConfig())

    def tearDown(self):
        self.dp = None

    def test_natural_parse(self):

        self.assertTrue(self.dp.natural_parse("yesterday"))
        self.assertTrue(self.dp.natural_parse("tomorrow"))
        self.assertTrue(self.dp.natural_parse("next week"))
        self.assertTrue(self.dp.natural_parse("last week"))

        self.assertFalse(self.dp.natural_parse("snuffalupagus"))

    def test_parseWithStringTooShortYieldsNothing(self):
        count = 0
        for result in self.dp.parse('Mar'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseWithNaturalStringYieldsSuccess(self):
        count = 0
        for result in self.dp.parse('yesterday'):
            count += 1
            self.assertEqual(result.subtype, 'Date')
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseShortSimpleDates(self):
        count = 0
        for result in self.dp.parse('1/10'):
            count += 1
            self.assertEqual(result.subtype, 'Date')
            self.assertEqual(result.confidence, 6)
        self.assertEqual(count, 1)

        count = 0
        for result in self.dp.parse('11/10'):
            count += 1
            self.assertEqual(result.subtype, 'Date')
            self.assertEqual(result.confidence, 53)
        self.assertEqual(count, 1)

        count = 0
        for result in self.dp.parse('08/11/2010'):
            count += 1
            self.assertEqual(result.subtype, 'Date')
            self.assertEqual(result.confidence, 154)
        self.assertEqual(count, 1)

    def test_NonDateYieldsNothing(self):
        count = 0
        for result in self.dp.parse('asdf;lkj'):
            count += 1
        self.assertEqual(count, 0)
