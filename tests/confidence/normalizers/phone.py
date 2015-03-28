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
from cahoots.confidence.normalizers.phone import PhoneWithUri
from cahoots.result import ParseResult
import unittest


class PhoneWithUriTests(unittest.TestCase):

    def test_test(self):
        self.assertFalse(PhoneWithUri.test(
            ['Phone', 'Boolean'], []
        ))
        self.assertTrue(PhoneWithUri.test(
            ['Phone', 'URI'], []
        ))

    def test_normalizer(self):
        eq_result = ParseResult('Phone', None, 90)
        uri_result = ParseResult('URI', None, 80)

        results = PhoneWithUri.normalize([eq_result, uri_result])

        count = 0
        for res in results:
            if res.type == 'Phone':
                count += 1
                self.assertEqual(res.confidence, 65)
            elif res.type == "URI":
                count += 1
                self.assertEqual(res.confidence, 80)

        self.assertEqual(count, len(results))
