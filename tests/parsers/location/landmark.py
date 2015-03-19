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
from cahoots.parsers.location.landmark import LandmarkParser
from tests.parsers.location import SQLite3Mock
from SereneRegistry import registry
from tests.config import TestConfig
import unittest
import sqlite3
import mock


class LandmarkParserTests(unittest.TestCase):

    lp = None

    def setUp(self):
        LandmarkParser.bootstrap(TestConfig())
        self.lp = LandmarkParser(TestConfig())

    def tearDown(self):
        SQLite3Mock.reset()
        registry.flush()
        self.lp = None

    def test_parse_longer_than_75_chars(self):
        test_string = 'asdfgasdfgasdfgasdfgasdfgasdfgasdfgasdfgasdfgasdfg' + \
            'asdfgasdfgasdfgasdfgasdfgasdfgasdfgasdfg'

        result = self.lp.parse(test_string)

        count = 1
        for _ in result:
            count += 2

        self.assertEqual(1, count)

    def test_parse_with_invalid_words(self):
        result = self.lp.parse('abc123 def456')

        count = 1
        for _ in result:
            count += 2

        self.assertEqual(1, count)

    def test_parse_with_invalid_characters(self):
        result = self.lp.parse('The E|n|d')

        count = 1
        for _ in result:
            count += 2

        self.assertEqual(1, count)

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parse_with_sqlite3_error(self):
        SQLite3Mock.fetchall_returns = [sqlite3.Error('Error')]
        result = self.lp.parse('The End Of Time')

        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (
                    'SELECT * FROM landmark WHERE resource like ?',
                    ('%End Of Time%',)
                )
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parse(self):
        SQLite3Mock.fetchall_returns = [
            [('us', 'united states')],
            [
                ('a', 'b', 'c', 'd', 'e', 'f'),
            ]
        ]

        results = self.lp.parse('The End Of Time')

        count = 0
        for result in results:
            self.assertEqual(result.result_value, [
                {
                    "city": "c",
                    "resource": "a",
                    "country": {
                        "abbreviation": "US",
                        "name": "United States"
                    },
                    "county": "d",
                    "state": "e",
                    "address": "b"
                }
            ])
            self.assertEqual(result.confidence, 95)
            count += 1
        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (
                    'SELECT * FROM landmark WHERE resource like ?',
                    ('%End Of Time%',)
                ),
                ('SELECT * FROM country WHERE abbreviation = ?', ('f',))
            ]
        )
        self.assertEqual(1, count)
