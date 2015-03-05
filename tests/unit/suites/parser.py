from cahoots.parser import ParserThread
from cahoots.parsers.base import BaseParser
from cahoots.result import ParseResult
from tests.unit.config import TestConfig
import unittest


class FakeModule(BaseParser):

    def __init__(self, config):
        BaseParser.__init__(self, config, "Fake")

    def parse(self, data, **kwargs):
        yield self.result("Subtype", 200, data)


class parserThreadTests(unittest.TestCase):

    parserThread = None

    def setUp(self):
        self.parserThread = ParserThread(TestConfig, FakeModule, 'datastring')

    def test_parserThreadYieldsResultAsExpected(self):
        self.parserThread.start()
        self.parserThread.join()

        for result in self.parserThread.results:
            self.assertIsInstance(result, ParseResult)
            self.assertEqual('Fake', result.Type)
            self.assertEqual('Subtype', result.Subtype)
            self.assertEqual(200, result.Confidence)
            self.assertEqual('datastring', result.ResultValue)
