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
from cahoots.confidence.normalizers.number import \
    NumberWithNonNumbers, IntOctWithPhoneDatePostalCode
from cahoots.result import ParseResult
import unittest


class NumberWithNonNumbersTests(unittest.TestCase):

    def test_test(self):
        self.assertTrue(
            NumberWithNonNumbers.test(['Date', 'Number'], [])
        )
        self.assertFalse(
            NumberWithNonNumbers.test(['Date', 'Postal Code'], [])
        )

    def test_normalize(self):
        result = ParseResult('Number', None, 70)

        results = NumberWithNonNumbers.normalize([result])

        count = 0
        for res in results:
            count += 1
            self.assertEqual(res.confidence, 35)

        self.assertEqual(count, len(results))


class IntOctWithPhoneDatePostalCodeTests(unittest.TestCase):

    def test_test(self):
        self.assertFalse(IntOctWithPhoneDatePostalCode.test(
            [],
            ['Number', 'Integer', 'Octal']
        ))
        self.assertTrue(IntOctWithPhoneDatePostalCode.test(
            [],
            ['Integer', 'Octal', 'Date']
        ))

    def test_normalize(self):
        results = [
            ParseResult('Number', 'Integer', 100),
            ParseResult('Number', 'Octal', 25),
            ParseResult('Date', 'Date', 50)
        ]

        results = IntOctWithPhoneDatePostalCode.normalize(results)

        count = 0
        for res in results:
            count += 1
            if res.subtype == 'Integer':
                self.assertEqual(10, res.confidence)
            elif res.subtype == 'Octal':
                self.assertEqual(5, res.confidence)
            else:
                self.assertEqual(50, res.confidence)

        self.assertEqual(count, 3)
