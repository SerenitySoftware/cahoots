from cahoots.parsers.base import BaseParser
from cahoots.result import ParseResult
from tests.unit.config import TestConfig
import unittest


class BaseParserTests(unittest.TestCase):
    """Unit Testing of the BaseParser"""

    bp = None

    def setUp(self):
        self.bp = BaseParser(TestConfig())

    def tearDown(self):
        self.bp = None

    def test_parse(self):

        self.assertRaises(NotImplementedError, self.bp.parse, "")

    def test_result(self):

        self.assertIsInstance(self.bp.result(), ParseResult)
