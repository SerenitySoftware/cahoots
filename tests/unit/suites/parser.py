from cahoots.config import BaseConfig
from cahoots.parser import ParserThread, CahootsParser
from cahoots.parsers.base import BaseParser
from cahoots.result import ParseResult
from tests.unit.config import TestConfig
import datetime
import mock
import unittest


class FakeModule(BaseParser):

    bootstrappingComplete = False

    def __init__(self, config):
        BaseParser.__init__(self, config, "Fake")

    def parse(self, data, **kwargs):
        yield self.result("Subtype", 200, data)

    @staticmethod
    def bootstrap(config):
        FakeModule.bootstrappingComplete = True


class ParserTestConfig(BaseConfig):

    debug = True

    enabledModules = [
        FakeModule,
    ]


class parserThreadTests(unittest.TestCase):

    parserThread = None

    def setUp(self):
        self.parserThread = ParserThread(TestConfig, FakeModule, 'data_string')

    def test_parserThreadYieldsResultAsExpected(self):
        self.parserThread.start()
        self.parserThread.join()

        for result in self.parserThread.results:
            self.assertIsInstance(result, ParseResult)
            self.assertEqual('Fake', result.Type)
            self.assertEqual('Subtype', result.Subtype)
            self.assertEqual(200, result.Confidence)
            self.assertEqual('data_string', result.ResultValue)


class FakeDate(datetime.datetime):
    def __new__(cls, *args, **kwargs):
        return datetime.datetime.__new__(datetime.datetime, *args, **kwargs)


class CahootsParserTests(unittest.TestCase):

    def test_bootstrapSetsUpParserProperly(self):
        CahootsParser(ParserTestConfig)
        self.assertTrue(FakeModule.bootstrappingComplete)
        FakeModule.bootstrappingComplete = False

    def test_parserCreatesInstanceOfBaseConfig(self):
        parser = CahootsParser(bootstrap=False)
        self.assertIsInstance(parser.Config, BaseConfig)

    def test_parserInstantiatesBaseConfig(self):
        parser = CahootsParser(BaseConfig(), False)
        self.assertIsInstance(parser.Config, BaseConfig)

    @mock.patch('datetime.datetime', FakeDate)
    def test_parserReturnsExpectedParserResult(self):
        FakeDate.now = classmethod(lambda cls: 'thetimeisnow')
        parser = CahootsParser(ParserTestConfig, False)
        result = parser.parse('data_string')

        self.assertEqual(4, len(result))
        self.assertEqual('data_string', result['query'])
        self.assertEqual('thetimeisnow', result['date'])
        self.assertIsInstance(result['top'], ParseResult)
        self.assertEqual(1, result['results']['count'])
        self.assertEqual(['Fake'], result['results']['types'])
        self.assertEqual(1, len(result['results']['matches']))
        self.assertIsInstance(result['results']['matches'][0], ParseResult)
