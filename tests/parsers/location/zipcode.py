# coding: utf-8
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
from cahoots.parsers.location.zipcode import ZipCodeParser
from tests.config import TestConfig
from SereneRegistry import registry
import unittest
import mock


class ZipCodeDatabaseMock(object):

    def __getitem__(self, data):
        result = registry.get('ZCPTest')

        if isinstance(result, IndexError):
            raise result

        return result


class ZipCodeStub(object):

    def __init__(self, loc):
        self.loc = loc


class ZipCodeParserTests(unittest.TestCase):
    """Unit testing of the zipcode parser"""

    zcp = None

    @mock.patch('pyzipcode.ZipCodeDatabase', ZipCodeDatabaseMock)
    def setUp(self):
        ZipCodeParser.bootstrap(TestConfig())
        self.zcp = ZipCodeParser(TestConfig())

    def tearDown(self):
        registry.flush()
        self.zcp = None

    def test_parseWithNonZipYieldsNothing(self):
        result = self.zcp.parse('abc123')
        count = 0
        for _ in result:
            count += 1
        self.assertEqual(0, count)

    def test_parseWith5DigitNonZipYieldsNothing(self):
        registry.set('ZCPTest', IndexError())
        result = self.zcp.parse('00000')
        count = 0
        for _ in result:
            count += 1
        self.assertEqual(0, count)

    def test_parseWith5DigitZipYieldsExpectedResult(self):
        registry.set('ZCPTest', ZipCodeStub('beverlyhills'))
        results = self.zcp.parse('90210')
        count = 0
        for result in results:
            count += 1
            self.assertEqual(result.subtype, 'Zip Code')
            self.assertEqual(result.result_value, {'loc': 'beverlyhills'})
            self.assertEqual(result.confidence, 95)
        self.assertEqual(1, count)

    def test_parseWith10DigitZipYieldsExpectedResult(self):
        registry.set('ZCPTest', ZipCodeStub('beverlyhills'))
        results = self.zcp.parse('90210-1210')
        count = 0
        for result in results:
            count += 1
            self.assertEqual(result.subtype, 'Zip Code')
            self.assertEqual(result.result_value, {'loc': 'beverlyhills'})
            self.assertEqual(result.confidence, 90)
        self.assertEqual(1, count)
