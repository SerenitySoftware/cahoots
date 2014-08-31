from cahoots.parsers.grammar import GrammarParser
from tests.unit.config import TestConfig
import unittest


class GrammarParserTests(unittest.TestCase):
    """Unit testing of the grammar parser"""

    gp = None

    def setUp(self):
        GrammarParser.bootstrap(TestConfig())
        self.gp = GrammarParser(TestConfig())

    def tearDown(self):
        self.gp = None

    def test_parseYieldsNothing(self):
        result = self.gp.parse('')
        self.assertIsNone(result)
