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
import sqlite3
from cahoots.parsers.location.postalcode import PostalCodeParser
from tests.parsers.location import SQLite3Mock
from tests.config import TestConfig
from SereneRegistry import registry
import unittest
import mock


class PostalCodeParserTests(unittest.TestCase):
    """Unit testing of the postalcode parser"""

    zcp = None

    def setUp(self):
        PostalCodeParser.bootstrap(TestConfig())
        self.zcp = PostalCodeParser(TestConfig())

    def tearDown(self):
        SQLite3Mock.reset()
        registry.flush()
        self.zcp = None

    def test_parseWithNonPostalYieldsNothing(self):
        result = self.zcp.parse('abc123')
        count = 0
        for _ in result:
            count += 1
        self.assertEqual(0, count)

    def test_parseWithTooLongNonPostalYieldsNothing(self):
        result = self.zcp.parse('abc123abc123abc123abc123abc123')
        count = 0
        for _ in result:
            count += 1
        self.assertEqual(0, count)

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parseWith5DigitNonPostalYieldsNothing(self):
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
    def test_postal_code_handles_errors_properly(self):
        SQLite3Mock.fetchall_returns = [sqlite3.Error('Error')]
        result = self.zcp.get_postal_code_data('21901')

        self.assertIsNone(result)
        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                ('SELECT * FROM city WHERE postal_code = ?', ('21901',))
            ]
        )

        SQLite3Mock.reset()
        SQLite3Mock.fetchall_returns = [
            sqlite3.Error('Error'),
            ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'),
        ]
        result = self.zcp.get_postal_code_data('21901-2000')

        self.assertIsNone(result)
        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                ('SELECT * FROM city WHERE postal_code = ?', ('21901-2000',)),
                ('SELECT * FROM city WHERE postal_code = ?', ('21901',))
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parseWith5DigitPostalYieldsExpectedResult(self):
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
    def test_parseWith10DigitPostalYieldsExpectedResult(self):
        SQLite3Mock.fetchall_returns = [
            [('us', 'united states')],
            [],
            [('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l')]
        ]
        results = self.zcp.parse('90210-1210')
        count = 0
        for result in results:
            count += 1
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
                ('SELECT * FROM city WHERE postal_code = ?', ('90210-1210',)),
                ('SELECT * FROM city WHERE postal_code = ?', ('90210',)),
                ('SELECT * FROM country WHERE abbreviation = ?', ('a',))
            ]
        )

    def test_postal_code_patterns_match(self):
        postal_regex = registry.get('ZCP_postal_code_regex')
        self.assertTrue(postal_regex.match('A999'))
        self.assertTrue(postal_regex.match('AB 12'))
        self.assertTrue(postal_regex.match('AD999'))
        self.assertTrue(postal_regex.match('999 99'))
        self.assertTrue(postal_regex.match('AA9999'))
        self.assertTrue(postal_regex.match('VC9999'))
        self.assertTrue(postal_regex.match('VG1199'))
        self.assertTrue(postal_regex.match('6799 W3'))
        self.assertTrue(postal_regex.match('9999 AA'))
        self.assertTrue(postal_regex.match('9999 AW'))
        self.assertTrue(postal_regex.match('9999 CW'))
        self.assertTrue(postal_regex.match('A9A 9A9'))
        self.assertTrue(postal_regex.match('AZ 9999'))
        self.assertTrue(postal_regex.match('BB99999'))
        self.assertTrue(postal_regex.match('GY9 9AA'))
        self.assertTrue(postal_regex.match('JE9 9AA'))
        self.assertTrue(postal_regex.match('JMAAA99'))
        self.assertTrue(postal_regex.match('LV-9999'))
        self.assertTrue(postal_regex.match('A9999AAA'))
        self.assertTrue(postal_regex.match('AA99 9AA'))
        self.assertTrue(postal_regex.match('AAA 9999'))
        self.assertTrue(postal_regex.match('AAAA 1ZZ'))
        self.assertTrue(postal_regex.match('FIQQ 1ZZ'))
        self.assertTrue(postal_regex.match('TKCA 1ZZ'))
        self.assertTrue(postal_regex.match('GX99 9AA'))
        self.assertTrue(postal_regex.match('IM99 9AA'))
        self.assertTrue(postal_regex.match('KY9-9999'))
        self.assertTrue(postal_regex.match('999'))
        self.assertTrue(postal_regex.match('9999'))
        self.assertTrue(postal_regex.match('99-99'))
        self.assertTrue(postal_regex.match('99-999'))
        self.assertTrue(postal_regex.match('999999'))
        self.assertTrue(postal_regex.match('999-999'))
        self.assertTrue(postal_regex.match('9999999'))
        self.assertTrue(postal_regex.match('999-9999'))
        self.assertTrue(postal_regex.match('9999-999'))
        self.assertTrue(postal_regex.match('99999-9999'))
        self.assertTrue(postal_regex.match('77515 CEDEX'))
        self.assertTrue(postal_regex.match('77515 CEDEX 9'))
        self.assertTrue(postal_regex.match('77515 CEDEX 99'))
