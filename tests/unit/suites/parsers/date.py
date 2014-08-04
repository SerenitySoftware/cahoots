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
