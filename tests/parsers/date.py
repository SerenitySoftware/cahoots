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
from cahoots.parsers.date import DateParser
from tests.config import TestConfig
import unittest


class DateParserTests(unittest.TestCase):
    """Unit Testing of the DateParser"""

    dp = None

    def setUp(self):
        self.dp = DateParser(TestConfig())

    def tearDown(self):
        self.dp = None

    def test_natural_parse(self):

        self.assertTrue(self.dp.natural_parse("yesterday"))
        self.assertTrue(self.dp.natural_parse("tomorrow"))
        self.assertTrue(self.dp.natural_parse("next week"))
        self.assertTrue(self.dp.natural_parse("last week"))

        self.assertFalse(self.dp.natural_parse("snuffalupagus"))

    def test_parseWithStringTooShortYieldsNothing(self):
        count = 0
        for _ in self.dp.parse('Mar'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseWithNaturalStringYieldsSuccess(self):
        count = 0
        for result in self.dp.parse('yesterday'):
            count += 1
            self.assertEqual(result.subtype, 'Date')
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseShortSimpleDates(self):
        count = 0
        for result in self.dp.parse('1/10'):
            count += 1
            self.assertEqual(result.subtype, 'Date')
            self.assertEqual(result.confidence, 6)
        self.assertEqual(count, 1)

        count = 0
        for result in self.dp.parse('11/10'):
            count += 1
            self.assertEqual(result.subtype, 'Date')
            self.assertEqual(result.confidence, 53)
        self.assertEqual(count, 1)

        count = 0
        for result in self.dp.parse('08/11/2010'):
            count += 1
            self.assertEqual(result.subtype, 'Date')
            self.assertEqual(result.confidence, 154)
        self.assertEqual(count, 1)

    def test_NonDateYieldsNothing(self):
        count = 0
        for _ in self.dp.parse('asdf;lkj'):
            count += 1
        self.assertEqual(count, 0)

    def test_OutOfRangePhoneNumberYieldsNothing(self):
        count = 0
        for _ in self.dp.parse('7052383102'):
            count += 1
        self.assertEqual(count, 0)
