from brain.parsers.date import DateParser
import unittest

class DateParserTests(unittest.TestCase):
    """Unit Testing of the DateParser"""

    dp = None

    def setUp(self):
        self.dp = DateParser()

    def tearDown(self):
        self.dp = None

    def test_naturalParse(self):

        self.assertTrue(self.dp.naturalParse("yesterday"))
        self.assertTrue(self.dp.naturalParse("tomorrow"))
        self.assertTrue(self.dp.naturalParse("next week"))
        self.assertTrue(self.dp.naturalParse("last week"))

        self.assertFalse(self.dp.naturalParse("snuffalupagus"))