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
from cahoots.parsers.location import \
    LocationDatabase, CityEntity, CountryEntity, StreetSuffixEntity
from SereneRegistry import registry
import unittest
import mock


class SQLite3Mock(object):

    execute_calls = []
    fetchall_returns = []

    @staticmethod
    def reset():
        SQLite3Mock.execute_calls = []
        SQLite3Mock.fetchall_returns = []

    @staticmethod
    def execute(sql, params=None):
        SQLite3Mock.execute_calls.append((sql, params))
        return SQLite3Mock

    @staticmethod
    def fetchall():
        value = SQLite3Mock.fetchall_returns.pop()
        if isinstance(value, BaseException):
            raise value
        else:
            return value

    @staticmethod
    # pylint: disable=unused-argument
    def connect(db_file):
        return SQLite3Mock

    @staticmethod
    def cursor():
        return SQLite3Mock

    @staticmethod
    def close():
        return SQLite3Mock


class LocationDatabaseTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        SQLite3Mock.reset()
        registry.flush()

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_select(self):
        ldb = LocationDatabase()
        with self.assertRaises(TypeError):
            ldb.single_select('sql', 'burp', CityEntity)

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_select_returns_expected_data(self):
        SQLite3Mock.fetchall_returns = [
            sqlite3.Error('Error'),
            [],
            [('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l')],
            [('us', 'united states')]
        ]

        ldb = LocationDatabase()

        # Country Result
        result = ldb.single_select('sql1', ('tuple1',), CountryEntity)
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], CountryEntity)
        self.assertEqual(result[0].abbreviation, 'us')
        self.assertEqual(result[0].name, 'united states')

        # City Result
        result = ldb.single_select('sql2', ('tuple2',), CityEntity)
        self.assertIsInstance(result, list)
        self.assertEqual(1, len(result))
        self.assertIsInstance(result[0], CityEntity)
        self.assertEqual(result[0].country, 'a')
        self.assertEqual(result[0].postal_code, 'b')
        self.assertEqual(result[0].city, 'c')
        self.assertEqual(result[0].state1, 'd')
        self.assertEqual(result[0].state2, 'e')
        self.assertEqual(result[0].province1, 'f')
        self.assertEqual(result[0].province2, 'g')
        self.assertEqual(result[0].community1, 'h')
        self.assertEqual(result[0].community2, 'i')
        self.assertEqual(result[0].latitude, 'j')
        self.assertEqual(result[0].longitude, 'k')
        self.assertEqual(result[0].coord_accuracy, 'l')

        # No results
        result = ldb.single_select('sql3', ('tuple3',), CityEntity)
        self.assertIsNone(result)

        # Error while fetching
        result = ldb.single_select('sql4', ('tuple4',), CountryEntity)
        self.assertIsNone(result)

        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                ('PRAGMA temp_store = 2', None),
                ('sql1', ('tuple1',)),
                ('PRAGMA temp_store = 2', None),
                ('sql2', ('tuple2',)),
                ('PRAGMA temp_store = 2', None),
                ('sql3', ('tuple3',)),
                ('PRAGMA temp_store = 2', None),
                ('sql4', ('tuple4',)),
            ]
        )

    def test_hydrate_with_non_lists(self):
        data = ('US',)
        result = LocationDatabase.hydrate(data, StreetSuffixEntity)
        self.assertIsInstance(result, StreetSuffixEntity)

        with self.assertRaises(TypeError):
            LocationDatabase.hydrate('foo', StreetSuffixEntity)
