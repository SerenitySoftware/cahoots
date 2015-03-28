"""
The MIT License (MIT)

Copyright (c) Serenity Software, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# pylint: disable=invalid-name,too-many-public-methods,missing-docstring
from cahoots.config import BaseConfig
from cahoots.parser import ParserThread, CahootsParser
from cahoots.parsers.base import BaseParser
from cahoots.result import ParseResult
from tests.config import TestConfig
import datetime
import mock
import unittest


class FakeModule(BaseParser):

    bootstrappingComplete = False

    def __init__(self, config):
        BaseParser.__init__(self, config, "Fake")

    def parse(self, data):
        yield self.result("Subtype", 200, data)

    @staticmethod
    def bootstrap(config):
        FakeModule.bootstrappingComplete = True


class ParserTestConfig(BaseConfig):

    debug = True

    enabled_modules = [
        FakeModule,
    ]

    enabled_confidence_normalizers = [
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
            self.assertEqual('Fake', result.type)
            self.assertEqual('Subtype', result.subtype)
            self.assertEqual(200, result.confidence)
            self.assertEqual('data_string', result.result_value)


class FakeDate(datetime.datetime):
    def __new__(cls):
        return datetime.datetime.__new__(datetime.datetime)


class CahootsParserTests(unittest.TestCase):

    def test_bootstrapSetsUpParserProperly(self):
        CahootsParser(ParserTestConfig, True)
        self.assertTrue(FakeModule.bootstrappingComplete)
        FakeModule.bootstrappingComplete = False

    def test_parserCreatesInstanceOfBaseConfig(self):
        parser = CahootsParser()
        self.assertIsInstance(parser.config, BaseConfig)

    def test_parserInstantiatesBaseConfig(self):
        parser = CahootsParser(BaseConfig())
        self.assertIsInstance(parser.config, BaseConfig)

    @mock.patch('datetime.datetime', FakeDate)
    def test_parserReturnsExpectedParserResult(self):
        FakeDate.now = classmethod(lambda cls: 'thetimeisnow')
        parser = CahootsParser(ParserTestConfig)
        result = parser.parse('data_string')

        self.assertEqual(5, len(result))
        self.assertEqual('data_string', result['query'])
        self.assertEqual('thetimeisnow', result['date'])
        self.assertIsInstance(result['top'], ParseResult)
        self.assertEqual(1, result['results']['count'])
        self.assertEqual(['Fake'], result['results']['types'])
        self.assertEqual(1, len(result['results']['matches']))
        self.assertIsInstance(result['results']['matches'][0], ParseResult)
