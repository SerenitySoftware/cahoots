from cahoots.parsers.location import LocationParser
from tests.unit.config import TestConfig
import unittest


class LocationParserTests(unittest.TestCase):
    """Unit testing of the location parser"""

    lp = None

    def setUp(self):
        LocationParser.bootstrap(TestConfig())
        self.lp = LocationParser(TestConfig())

    def tearDown(self):
        self.lp = None

    def test_parseYieldsNothing(self):
        result = self.lp.parse('')
        self.assertIsNone(result)
