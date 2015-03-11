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
from tests.parsers.location import SQLite3Mock
from tests.config import TestConfig
from SereneRegistry import registry
import unittest
import mock


class ZipCodeParserTests(unittest.TestCase):
    """Unit testing of the zipcode parser"""

    zcp = None

    def setUp(self):
        ZipCodeParser.bootstrap(TestConfig())
        self.zcp = ZipCodeParser(TestConfig())

    def tearDown(self):
        SQLite3Mock.reset()
        registry.flush()
        self.zcp = None

    def test_parseWithNonZipYieldsNothing(self):
        result = self.zcp.parse('abc123')
        count = 0
        for _ in result:
            count += 1
        self.assertEqual(0, count)

    def test_parseWithTooLongNonZipYieldsNothing(self):
        result = self.zcp.parse('abc123abc123abc123abc123abc123')
        count = 0
        for _ in result:
            count += 1
        self.assertEqual(0, count)

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parseWith5DigitNonZipYieldsNothing(self):
        SQLite3Mock.fetchall_returns = [[]]
        result = self.zcp.parse('00000')
        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)
        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                ('SELECT * FROM city WHERE postal_code = ?', ('00000',))
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parseWith5DigitZipYieldsExpectedResult(self):
        SQLite3Mock.fetchall_returns = [
            [('us', 'united states')],
            [('us', 'united states')],
            [
                ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'),
                ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'),
            ]
        ]
        results = self.zcp.parse('90210')
        count = 0
        for result in results:
            count += 1
            self.assertEqual(result.subtype, 'Standard')
            self.assertEqual(result.result_value, [
                {
                    "province1": "f",
                    "city": "c",
                    "province2": "g",
                    "country": {
                        "abbreviation": "US",
                        "name": "United States"
                    },
                    "community2": "i",
                    "community1": "h",
                    "state2": "e",
                    "state1": "d",
                    "coord_accuracy": "l",
                    "postal_code": "b",
                    "longitude": "k",
                    "latitude": "j"
                },
                {
                    "province1": "f",
                    "city": "c",
                    "province2": "g",
                    "country": {
                        "abbreviation": "US",
                        "name": "United States"
                    },
                    "community2": "i",
                    "community1": "h",
                    "state2": "e",
                    "state1": "d",
                    "coord_accuracy": "l",
                    "postal_code": "b",
                    "longitude": "k",
                    "latitude": "j"
                }
            ])
            self.assertEqual(result.confidence, 79)
        self.assertEqual(1, count)
        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                ('SELECT * FROM city WHERE postal_code = ?', ('90210',)),
                ('SELECT * FROM country WHERE abbreviation = ?', ('a',)),
                ('SELECT * FROM country WHERE abbreviation = ?', ('a',))
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parseWith10DigitZipYieldsExpectedResult(self):
        SQLite3Mock.fetchall_returns = [
            [('us', 'united states')],
            [('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l')]
        ]
        results = self.zcp.parse('90210-1210')
        count = 0
        for result in results:
            count += 1
            self.assertEqual(result.subtype, 'Plus Four')
            self.assertEqual(result.result_value, [
                {
                    "province1": "f",
                    "city": "c",
                    "province2": "g",
                    "country": {
                        "abbreviation": "US",
                        "name": "United States"
                    },
                    "community2": "i",
                    "community1": "h",
                    "state2": "e",
                    "state1": "d",
                    "coord_accuracy": "l",
                    "postal_code": "b",
                    "longitude": "k",
                    "latitude": "j"
                }
            ])
            self.assertEqual(result.confidence, 90)
        self.assertEqual(1, count)
        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                ('SELECT * FROM city WHERE postal_code = ?', ('90210',)),
                ('SELECT * FROM country WHERE abbreviation = ?', ('a',))
            ]
        )
