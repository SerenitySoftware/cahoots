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
from cahoots.result import ParseResult


class DateWithPostalCode(BaseNormalizer):
    """If we get a date and a postal code, the date gets higher confidence"""

    @staticmethod
    def test(types, _):
        """We want to normalize if there are Numbers as well as non numbers"""
        return 'Date' in types and 'Postal Code' in types

    @staticmethod
    def normalize(results):
        """If we don't just have numbers, we cut our confidence in half."""
        postal_code = None
        date = None

        for result in \
                [r for r in results if r.type in ['Date', 'Postal Code']]:

            if result.type == 'Date':
                date = result
            elif result.type == 'Postal Code':
                postal_code = result

        assert isinstance(date, ParseResult)
        assert isinstance(postal_code, ParseResult)

        date.confidence = min(70, postal_code.confidence+4)

        return results
