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
from cahoots.confidence.normalizers.character import CharacterWithoutBoolean
from cahoots.result import ParseResult
import unittest


class CharacterWithoutBooleanTests(unittest.TestCase):

    def test_test(self):
        self.assertFalse(CharacterWithoutBoolean.test(
            ['Character', 'Boolean'], []
        ))
        self.assertTrue(CharacterWithoutBoolean.test(
            ['Character', 'Postal Code'], []
        ))

    def test_normalizer_with_pc_conf_over_70(self):
        char_result = ParseResult('Character', None, 25)
        pc_result = ParseResult('Postal Code', None, 80)

        results = CharacterWithoutBoolean.normalize([char_result, pc_result])

        count = 0
        for res in results:
            if res.type == 'Character':
                count += 1
                self.assertEqual(res.confidence, 100)
            elif res.type == "Postal Code":
                count += 1
                self.assertEqual(res.confidence, 80)

        self.assertEqual(count, len(results))
