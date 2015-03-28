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


class EquationWithPhonePostalCode(BaseNormalizer):
    """Normalizes Equations scores if there's a phone/postal code present"""

    @staticmethod
    def test(types, _):
        """
        We want to normalize if there is an equation and a phone/postal code
        """
        return 'Equation' in types and \
               ('Postal Code' in types or 'Phone' in types)

    @staticmethod
    def normalize(results):
        """
        15 point confidence hit if this equation is also a phone/postal code
        """
        for result in [r for r in results if r.type == 'Equation']:
            result.confidence -= 15

        return results
