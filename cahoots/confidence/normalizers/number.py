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


class NumberNormalizer(object):
    """Normalizes Number Results"""

    @staticmethod
    def test(types):
        """We want to normalize if there are Numbers as well as non numbers"""
        others = [t for t in types if t != 'Number']
        return len(others) > 0 and len(others) != len(types)

    @staticmethod
    def normalize(results, types):
        """Significantly hitting Number results of certain types"""
        intersections = {
            'intoct': ['Postal Code', 'Date', 'Phone']
        }

        # Looking through all number subtypes and normalizing any results
        for result in [r for r in results if r.type == 'Number']:

            if result.subtype in ['Integer', 'Octal'] and \
                    set(intersections['intoct']).intersection(types):
                # Certain subtypes cause major reductions against int/octal
                result.confidence = \
                    5 if result.subtype == 'Octal' else 10

        return results
