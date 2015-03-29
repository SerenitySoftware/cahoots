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
from cahoots.parsers.character import CharacterParser
from tests.config import TestConfig
from cahoots.util import u
import unittest


class CharacterParserTests(unittest.TestCase):
    """Unit Testing of the CharacterParser"""

    cp = None

    def setUp(self):
        self.cp = CharacterParser(TestConfig())

    def tearDown(self):
        self.cp = None

    def test_is_letter(self):
        self.assertTrue(self.cp.is_letter("a"))
        self.assertFalse(self.cp.is_letter("1"))
        self.assertFalse(self.cp.is_letter("."))
        self.assertFalse(self.cp.is_letter(" "))
        self.assertFalse(self.cp.is_letter("asdf"))

    def test_is_punctuation(self):
        self.assertTrue(self.cp.is_punctuation("."))
        self.assertFalse(self.cp.is_punctuation("1"))
        self.assertFalse(self.cp.is_punctuation("a"))
        self.assertFalse(self.cp.is_punctuation(" "))
        self.assertFalse(self.cp.is_punctuation("asdf"))

    def test_is_whitespace(self):
        self.assertTrue(self.cp.is_whitespace(" "))
        self.assertFalse(self.cp.is_whitespace("1"))
        self.assertFalse(self.cp.is_whitespace("a"))
        self.assertFalse(self.cp.is_whitespace("."))
        self.assertFalse(self.cp.is_whitespace("asdf"))

    def test_parseReturnsNothingWithStringLongerThanOneCharacter(self):
        count = 0
        for _ in self.cp.parse("asdf"):
            count += 1
        self.assertEqual(count, 0)

    def test_parseNonAsciiCharacterReturnNone(self):
        count = 0
        # pylint: disable=anomalous-unicode-escape-in-string
        for _ in self.cp.parse(u('\u0080')):
            count += 1
        self.assertEqual(count, 0)

    def test_parseLetterYieldsProperResult(self):
        count = 0
        for result in self.cp.parse('a'):
            count += 1
            self.assertEqual(result.subtype, 'Letter')
            self.assertEqual(result.data, {'char-code': 97})
            self.assertEqual(result.confidence, 25)
        self.assertEqual(count, 1)

    def test_parsePunctuationYieldsProperResult(self):
        count = 0
        for result in self.cp.parse('.'):
            count += 1
            self.assertEqual(result.subtype, 'Punctuation')
            self.assertEqual(result.data, {'char-code': 46})
            self.assertEqual(result.confidence, 25)
        self.assertEqual(count, 1)

    def test_parseWhitespaceYieldsProperResult(self):
        count = 0
        for result in self.cp.parse(' '):
            count += 1
            self.assertEqual(result.subtype, 'Whitespace')
            self.assertEqual(result.data, {'char-code': 32})
            self.assertEqual(result.confidence, 25)
        self.assertEqual(count, 1)

    def test_parseBooleanLetterYieldsLowerConfidence(self):
        count = 0
        for result in self.cp.parse('T'):
            count += 1
            self.assertEqual(result.subtype, 'Letter')
            self.assertEqual(result.data, {'char-code': 84})
            self.assertEqual(result.confidence, 25)
        self.assertEqual(count, 1)
