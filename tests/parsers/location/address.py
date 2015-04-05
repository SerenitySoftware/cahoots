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
from cahoots.parsers.location import StreetSuffixEntity
from cahoots.parsers.location.address import AddressParser
from cahoots.parsers.name import NameParser
from cahoots.result import ParseResult
from tests.config import TestConfig
from tests.parsers.location import SQLite3Mock
from SereneRegistry import registry
import unittest
import mock
import sqlite3


class AddressParserTests(unittest.TestCase):

    ap = None

    def setUp(self):
        NameParser.bootstrap(TestConfig())
        AddressParser.bootstrap(TestConfig())
        self.ap = AddressParser(TestConfig())

    def tearDown(self):
        SQLite3Mock.reset()
        registry.flush()
        self.ap = None

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_get_street_suffix(self):
        SQLite3Mock.fetchall_returns = [('street',)]

        working_data = ['look', 'a', 'street']

        result = self.ap.get_street_suffix(working_data)

        self.assertIsInstance(result, StreetSuffixEntity)
        self.assertEqual(result.suffix_name, 'street')

        sql = 'SELECT * FROM street_suffix WHERE ' +\
              'suffix_name = ? or suffix_name = ? or suffix_name = ?'

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (sql, ('look', 'a', 'street')),
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_get_street_suffix_handles_errors_properly(self):
        SQLite3Mock.fetchall_returns = [sqlite3.Error("Error")]

        working_data = ['look', 'a', 'street']

        result = self.ap.get_street_suffix(working_data)

        self.assertIsNone(result)

        sql = 'SELECT * FROM street_suffix WHERE ' +\
              'suffix_name = ? or suffix_name = ? or suffix_name = ?'

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (sql, ('look', 'a', 'street')),
            ]
        )

    def test_separate_suspected_name(self):
        working_data = [
            'Barack',
            'and',
            'Michelle',
            'Obama',
            '1600'
        ]

        result = self.ap.separate_suspected_name(working_data)

        self.assertEqual((['1600'], 'Barack Michelle Obama'), result)

    def test_is_address_name(self):
        result = self.ap.is_address_name('Barack Michelle Obama')
        self.assertTrue(result)

        result = self.ap.is_address_name('not a name')
        self.assertFalse(result)

    def test_is_invalid_int(self):
        result = self.ap.is_invalid_int('123')
        self.assertTrue(result)
        result = self.ap.is_invalid_int('abc')
        self.assertFalse(result)
        result = self.ap.is_invalid_int('123456')
        self.assertFalse(result)

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_find_address_tokens(self):
        SQLite3Mock.fetchall_returns = [
            (0,),
            (20,),
            (0,)
        ]

        working_data = ['str1', 'str2']

        result = self.ap.find_address_tokens(
            working_data,
            {
                'street_suffix': None,
                'addressed_to': None,
                'address_tokens': []
            }
        )

        self.assertEqual(
            result,
            (
                1,
                {
                    'street_suffix': None,
                    'addressed_to': None,
                    'address_tokens': [
                        {
                            'token': 'str2',
                            'matches': 20
                        }
                    ]
                }
            )
        )

        sql = 'SELECT count(*) FROM city WHERE country = ? OR ' +\
              'postal_code = ? OR city = ? OR state1 = ? OR state2 = ?'

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (sql, ('str1', 'str1', 'str1', 'str1', 'str1')),
                (sql, ('str2', 'str2', 'str2', 'str2', 'str2')),
                (sql, (
                    'str1 str2',
                    'str1 str2',
                    'str1 str2',
                    'str1 str2',
                    'str1 str2'
                )),
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_find_address_tokens_handles_errors_properly(self):
        SQLite3Mock.fetchall_returns = [
            sqlite3.Error('Error'),
        ]

        working_data = ['str1']

        result = self.ap.find_address_tokens(working_data, [])

        self.assertEqual(result, (0, []))

        sql = 'SELECT count(*) FROM city WHERE country = ? OR ' +\
              'postal_code = ? OR city = ? OR state1 = ? OR state2 = ?'

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (sql, ('str1', 'str1', 'str1', 'str1', 'str1'))
            ]
        )

    def test_parse_with_data_too_long(self):
        result = self.ap.parse(
            'Lorem ipsum dolor sit amet, consectetur adipiscing' +
            ' elit. Curabitur dignissim feugiat quam, ut tempus nisi'
        )

        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)

    def test_parse_with_no_digits_in_data(self):
        result = self.ap.parse(
            'Lorem ipsum dolor sit amet, consectetur adipiscing' +
            'elit. Curabitur dignissim feugiat quam, ut'
        )

        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)

    def test_parse_with_too_few_words(self):
        result = self.ap.parse('Lorem 123, dolor')

        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)

    def test_parse_with_no_word_starting_with_digit(self):
        result = self.ap.parse('Lorem a123, dolor sit')

        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parse_with_no_street_suffix(self):
        SQLite3Mock.fetchall_returns = [None]

        result = self.ap.parse('Lorem 123, dolor sit')

        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)

        sql = 'SELECT * FROM street_suffix WHERE suffix_name = ? or ' +\
              'suffix_name = ? or suffix_name = ? or suffix_name = ?'

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (sql, ('Lorem', '123', 'dolor', 'sit')),
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parse_with_impossible_suffix_return(self):
        SQLite3Mock.fetchall_returns = [('street',)]

        result = self.ap.parse('Lorem 123, dolor sit')

        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)

        sql = 'SELECT * FROM street_suffix WHERE suffix_name = ? or ' +\
              'suffix_name = ? or suffix_name = ? or suffix_name = ?'

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (sql, ('Lorem', '123', 'dolor', 'sit')),
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parse_with_invalid_name_prefix(self):
        SQLite3Mock.fetchall_returns = [('street',)]

        result = self.ap.parse('lorem ipsum 123, dolor street')

        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)

        sql = 'SELECT * FROM street_suffix WHERE suffix_name = ? or ' +\
              'suffix_name = ? or suffix_name = ? or ' +\
              'suffix_name = ? or suffix_name = ?'

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (sql, ('lorem', 'ipsum', '123', 'dolor', 'street')),
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parse_with_no_address_tokens_found(self):
        SQLite3Mock.fetchall_returns = [
            (0,),
            (0,),
            ('street',)
        ]

        result = self.ap.parse('Lorem Ipsum 123, dolor street')

        count = 0
        for _ in result:
            count += 1

        self.assertEqual(0, count)

        ss_sql = 'SELECT * FROM street_suffix WHERE suffix_name = ? or ' +\
                 'suffix_name = ? or suffix_name = ? or ' +\
                 'suffix_name = ? or suffix_name = ?'

        city_sql = 'SELECT count(*) FROM city WHERE country = ? OR ' +\
                   'postal_code = ? OR city = ? OR state1 = ? OR state2 = ?'

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (ss_sql, ('Lorem', 'Ipsum', '123', 'dolor', 'street')),
                ('PRAGMA temp_store = 2', None),
                (city_sql, ('dolor', 'dolor', 'dolor', 'dolor', 'dolor')),
                (city_sql, (
                    '123 dolor',
                    '123 dolor',
                    '123 dolor',
                    '123 dolor',
                    '123 dolor'
                ))
            ]
        )

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parse_yields_expected_result(self):
        SQLite3Mock.fetchall_returns = [
            (0,),
            (1,),
            ('street',)
        ]

        result = self.ap.parse('Lorem Ipsum 123, dolor street')

        count = 0
        for res in result:
            self.assertIsInstance(res, ParseResult)
            self.assertEqual(res.subtype, 'With Addressee')
            self.assertEqual(res.confidence, 40)
            self.assertEqual(
                res.result_value,
                {
                    'street_suffix': 'street',
                    'addressed_to': 'Lorem Ipsum',
                    'address_tokens': [
                        {
                            'token': 'dolor',
                            'matches': 1
                        }
                    ]
                }
            )
            count += 1

        self.assertEqual(1, count)

        ss_sql = 'SELECT * FROM street_suffix WHERE suffix_name = ? or ' +\
                 'suffix_name = ? or suffix_name = ? or ' +\
                 'suffix_name = ? or suffix_name = ?'

        city_sql = 'SELECT count(*) FROM city WHERE country = ? OR ' +\
                   'postal_code = ? OR city = ? OR state1 = ? OR state2 = ?'

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                (ss_sql, ('Lorem', 'Ipsum', '123', 'dolor', 'street')),
                ('PRAGMA temp_store = 2', None),
                (city_sql, ('dolor', 'dolor', 'dolor', 'dolor', 'dolor')),
                (city_sql, (
                    '123 dolor',
                    '123 dolor',
                    '123 dolor',
                    '123 dolor',
                    '123 dolor'
                ))
            ]
        )
