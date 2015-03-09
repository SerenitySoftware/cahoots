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
from cahoots.util import truncate_text, is_number, strings_intersect
import unittest


class TruncateTextTests(unittest.TestCase):

    testString = 'The quick brown fox jumps over the lazy dog'

    def test_too_short_string(self):
        self.assertEquals(truncate_text(self.testString), self.testString)

    def test_short_limit(self):
        self.assertEquals(truncate_text(self.testString, 10), 'The qui...')

    def test_too_long_string(self):
        testString = 'Lorem ipsum dolor sit amet, consectetur adipiscing' \
                     ' elit. Suspendisse non risus risus amet.'
        truncatedTestString = 'Lorem ipsum dolor sit amet, consectetur' \
                              ' adipiscing elit. Suspendisse non risu...'

        self.assertEquals(truncate_text(testString), truncatedTestString)


class IsNumberTests(unittest.TestCase):

    def test_is_number(self):

        self.assertTrue(is_number("123.123"))
        self.assertTrue(is_number("123"))

        self.assertFalse(is_number("7 divided by 2"))


class StringsIntersectTests(unittest.TestCase):

    def test_strings_intersect(self):

        self.assertFalse(strings_intersect("abc", "def"))

        self.assertTrue(strings_intersect("abc", "cde"))
