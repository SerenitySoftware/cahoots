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

    def test_naturalParse(self):

        self.assertTrue(self.dp.naturalParse("yesterday"))
        self.assertTrue(self.dp.naturalParse("tomorrow"))
        self.assertTrue(self.dp.naturalParse("next week"))
        self.assertTrue(self.dp.naturalParse("last week"))

        self.assertFalse(self.dp.naturalParse("snuffalupagus"))

    def test_parseWithStringTooShortYieldsNothing(self):
        count = 0
        for result in self.dp.parse('Mar'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseWithNaturalStringYieldsSuccess(self):
        count = 0
        for result in self.dp.parse('yesterday'):
            count += 1
            self.assertEqual(result.Subtype, 'Date')
            self.assertEqual(result.Confidence, 100)
        self.assertEqual(count, 1)

    def test_parseShortSimpleDates(self):
        count = 0
        for result in self.dp.parse('1/10'):
            count += 1
            self.assertEqual(result.Subtype, 'Date')
            self.assertEqual(result.Confidence, 6)
        self.assertEqual(count, 1)

        count = 0
        for result in self.dp.parse('11/10'):
            count += 1
            self.assertEqual(result.Subtype, 'Date')
            self.assertEqual(result.Confidence, 53)
        self.assertEqual(count, 1)

        count = 0
        for result in self.dp.parse('08/11/2010'):
            count += 1
            self.assertEqual(result.Subtype, 'Date')
            self.assertEqual(result.Confidence, 154)
        self.assertEqual(count, 1)

    def test_NonDateYieldsNothing(self):
        count = 0
        for result in self.dp.parse('asdf;lkj'):
            count += 1
        self.assertEqual(count, 0)
