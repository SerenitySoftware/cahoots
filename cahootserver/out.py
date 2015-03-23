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
# pylint: disable=method-hidden
from datetime import date, datetime
from cahoots.result import ParseResult
import simplejson


class CahootsEncoder(simplejson.JSONEncoder):
    """Handles the encoding of various special types related to cahoots"""

    def default(self, obj):
        """encodes cahoots special types"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, ParseResult):
            return {
                'type': obj.type,
                'subtype': obj.subtype,
                'confidence': obj.confidence,
                'value': obj.result_value,
                'data': obj.data
            }

        return super(CahootsEncoder, self).default(obj)


def encode(data):
    """calls simplejson's encoding stuff with our needs"""
    return simplejson.dumps(
        data,
        cls=CahootsEncoder,
        ensure_ascii=False,
        encoding='utf8',
        indent=4
    )
