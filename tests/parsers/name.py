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
from cahoots.parsers.name import NameParser
from tests.config import TestConfig
from cahoots.util import u
from SereneRegistry import registry
import unittest


class NameParserTests(unittest.TestCase):
    """Unit Testing of the NameParser"""

    np = None

    def setUp(self):
        NameParser.bootstrap(TestConfig())
        self.np = NameParser(TestConfig())

    def tearDown(self):
        registry.flush()
        self.np = None

    def test_basic_validation(self):

        self.assertFalse(self.np.basic_validation(['foo', 'Bar', '2nd']))
        self.assertFalse(self.np.basic_validation(['Foo', 'Bar', 'a123']))
        self.assertFalse(self.np.basic_validation(['Foo', 'Bar', '$123']))
        self.assertFalse(self.np.basic_validation(['Foo', 'Bar', '123']))

        self.assertTrue(self.np.basic_validation(['Foo', 'Bar', '2nd']))

    def test_is_prefix(self):

        self.assertFalse(self.np.is_prefix('foo'))

        self.assertTrue(self.np.is_prefix('Mr'))

    def test_is_suffix(self):

        self.assertFalse(self.np.is_suffix('foo'))

        self.assertTrue(self.np.is_suffix('Sr'))
        self.assertTrue(self.np.is_suffix('IV'))

    def test_is_initial(self):

        self.assertFalse(self.np.is_initial('Hello'))
        self.assertFalse(self.np.is_initial('1'))
        self.assertFalse(self.np.is_initial('1.'))
        self.assertFalse(self.np.is_initial('1,'))
        self.assertFalse(self.np.is_initial('A,'))

        self.assertTrue(self.np.is_initial('Q'))
        self.assertTrue(self.np.is_initial('Q.'))

    def test_parseWithNoUpperCaseLettersYieldsNothing(self):
        count = 0
        for _ in self.np.parse('foo'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseWithGreaterThanTenWordsYieldsNothing(self):
        count = 0
        for _ in self.np.parse(
                'Foo bar baz buns barf blarg bleh bler blue sner sneh snaf.'
        ):
            count += 1
        self.assertEqual(count, 0)

    def test_parseWithNonBasicValidatedAttributesYieldsNothing(self):
        count = 0
        for _ in self.np.parse('Foo bar The Third'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseYieldsExpectedConfidenceWithFiveWordName(self):
        count = 0
        for result in self.np.parse('Dr. Foo Bar Bleh Bar Sr.'):
            self.assertEqual(result.confidence, 52)
            self.assertEqual(result.subtype, 'Name')
            count += 1
        self.assertEqual(count, 1)

    def test_parseYieldsExpectedConfidenceWithThreeWordName(self):
        count = 0
        for result in self.np.parse('Dr. Foo Q. Ben Sr.'):
            self.assertEqual(result.confidence, 95)
            self.assertEqual(result.subtype, 'Name')
            count += 1
        self.assertEqual(count, 1)

    def test_parseYieldsNothingWithOneWordName(self):
        count = 0
        for _ in self.np.parse('Foo'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseYieldsNothingWithNonPrintableCharacters(self):
        count = 0
        for _ in self.np.parse(u('40.244° N 79.123° W')):
            count += 1
        self.assertEqual(count, 0)
