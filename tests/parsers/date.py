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
from datetime import datetime, timedelta
from cahoots.parsers.date import DateParser
from tests.config import TestConfig
from SereneRegistry import registry
import pyparsing
import unittest


class DateParserTests(unittest.TestCase):
    """Unit Testing of the DateParser"""

    def setUp(self):
        DateParser.bootstrap(TestConfig())
        self.dp = DateParser(TestConfig())

    def tearDown(self):
        registry.flush()
        self.dp = None

    def test_bootstrap(self):
        self.assertTrue(registry.test('DP_pre_timedelta_phrases'))
        self.assertTrue(registry.test('DP_post_timedelta_phrases'))
        self.assertEqual(
            type(registry.get('DP_pre_timedelta_phrases')),
            pyparsing.And
        )
        self.assertEqual(
            type(registry.get('DP_post_timedelta_phrases')),
            pyparsing.Or
        )

    def test_simple_parses(self):
        results = self.dp.parse('today')
        count = 0
        for res in results:
            count += 1
            self.assertEqual(res.confidence, 100)
            self.assertEqual(res.subtype, 'Natural')
            self.assertIsInstance(res.result_value, datetime)
        self.assertEqual(1, count)

        results = self.dp.parse('2014-03-23')
        count = 0
        for res in results:
            count += 1
            self.assertEqual(res.confidence, 100)
            self.assertEqual(res.subtype, 'Standard')
            self.assertIsInstance(res.result_value, datetime)
        self.assertEqual(1, count)

        results = self.dp.parse('FAELURE')
        count = 0
        for _ in results:
            count += 1
        self.assertEqual(0, count)

        results = self.dp.parse('NO')
        count = 0
        for _ in results:
            count += 1
        self.assertEqual(0, count)

    def test_pre_timedelta_parse(self):
        results = self.dp.parse('300 seconds before 2012')
        count = 0
        for res in results:
            count += 1
            self.assertEqual(res.confidence, 100)
            self.assertEqual(res.subtype, 'Number Timescale Preposition Date')
            self.assertIsInstance(res.result_value, datetime)
        self.assertEqual(1, count)

    def test_post_timedelta_parse(self):
        results = self.dp.parse('2012 plus 300 hours')
        count = 0
        for res in results:
            count += 1
            self.assertEqual(res.confidence, 100)
            self.assertEqual(res.subtype, 'Date Operator Number Timescale')
            self.assertIsInstance(res.result_value, datetime)

        self.assertEqual(1, count)
        results = self.dp.parse('2012 minus an hour')
        count = 0
        for res in results:
            count += 1
            self.assertEqual(res.confidence, 100)
            self.assertEqual(res.subtype, 'Date Operator Number Timescale')
            self.assertIsInstance(res.result_value, datetime)
        self.assertEqual(1, count)

    def test_determine_timescale_delta(self):
        results = [
            DateParser.determine_timescale_delta('microsecond', 1),
            DateParser.determine_timescale_delta('millisecond', 1),
            DateParser.determine_timescale_delta('second', 1),
            DateParser.determine_timescale_delta('minute', 1),
            DateParser.determine_timescale_delta('hour', 1),
            DateParser.determine_timescale_delta('day', 1),
            DateParser.determine_timescale_delta('week', 1),
            DateParser.determine_timescale_delta('year', 1),
            DateParser.determine_timescale_delta('asdf', 1)
        ]

        for res in results:
            self.assertIsInstance(res, timedelta)

    def test_natural_parse(self):
        results = [
            DateParser.natural_parse('now'),
            DateParser.natural_parse('today'),
            DateParser.natural_parse('tomorrow'),
            DateParser.natural_parse('yesterday'),
            DateParser.natural_parse('next week'),
            DateParser.natural_parse('last week'),
            DateParser.natural_parse('next year'),
            DateParser.natural_parse('last year'),
            DateParser.natural_parse('asdf')
        ]

        self.assertFalse(results.pop())

        for res in results:
            self.assertIsInstance(res, datetime)
