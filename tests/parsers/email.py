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
from cahoots.parsers.email import EmailParser
from tests.config import TestConfig
import unittest


class EmailParserTests(unittest.TestCase):
    """Unit Testing of the EmailParser"""

    ep = None

    def setUp(self):
        self.ep = EmailParser(TestConfig())

    def tearDown(self):
        self.ep = None

    def test_matches_email_pattern(self):
        self.assertTrue(self.ep.matches_email_pattern("foobar@photoflit.com"))
        self.assertTrue(self.ep.matches_email_pattern("foo+bar@photoflit.com"))
        self.assertTrue(self.ep.matches_email_pattern("foo.bar@gmail.com"))
        self.assertTrue(self.ep.matches_email_pattern("foo@photoflit.co.uk"))
        self.assertFalse(self.ep.matches_email_pattern("asdf@asdf"))
        self.assertFalse(self.ep.matches_email_pattern("asdfasdf"))

    def test_parseWithNoAtSymbolReturnsNothing(self):
        count = 0
        for _ in self.ep.parse("Foo"):
            count += 1
        self.assertEqual(0, count)

    def test_parseDeterminesEmailValidityProperly(self):
        count = 0
        for result in self.ep.parse("foo@bar.com"):
            count += 1
            self.assertEqual("Email Address", result.subtype)
            self.assertEqual(100, result.confidence)
        self.assertEqual(1, count)
