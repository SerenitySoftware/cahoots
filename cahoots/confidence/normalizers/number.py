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
from cahoots.confidence.normalizers.base import BaseNormalizer


class NumberWithNonNumbers(BaseNormalizer):
    """Normalizes All Number Results Where Non-Numbers Are Present"""

    @staticmethod
    def test(types, _):
        """We want to normalize if there are Numbers as well as non numbers"""
        others = [t for t in types if t != 'Number']
        return len(others) > 0 and len(others) != len(types)

    @staticmethod
    def normalize(results):
        """If we don't just have numbers, we cut our confidence in half."""
        for result in [r for r in results if r.type == 'Number']:
            result.confidence = int(result.confidence * 0.5)

        return results


class IntOctWithPhoneDatePostalCode(BaseNormalizer):
    """Normalizes Int/Oct where Phone, Date, or Postal Code Are Present"""

    @staticmethod
    def test(_, types):
        """We want to normalize if there are Numbers as well as non numbers"""
        intersections = {
            'alter': ['Integer', 'Octal'],
            'search': ['Postal Code', 'Date', 'Phone']
        }

        if set(intersections['alter']).intersection(types) and \
                set(intersections['search']).intersection(types):
            return True
        return False

    @staticmethod
    def normalize(results):
        """Significantly hitting items that qualify"""

        for result in \
                [r for r in results if r.subtype in ['Integer', 'Octal']]:

            result.confidence = \
                5 if result.subtype == 'Octal' else 10

        return results
