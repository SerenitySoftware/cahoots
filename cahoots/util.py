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
# pylint: disable=invalid-name
import sys
if sys.version_info[0] < 3:  # pragma: no cover
    import codecs


if sys.version_info[0] < 3:  # pragma: no cover
    def u(value):
        """returns unicode encoded value"""
        return codecs.unicode_escape_decode(value)[0]
else:  # pragma: no cover
    def u(value):
        """python3 version just returns value"""
        return value


def truncate_text(text, limit=80):
    '''truncates text to a provided length'''

    if len(text) > limit:
        text = text[:limit-3] + "..."
    return text


def is_number(text):
    """Checking if the text is a number"""

    try:
        float(text.strip())
    except ValueError:
        return False

    return True


def strings_intersect(s_one, s_two):
    """Checks if two strings have any intersections"""
    return not set(s_one).isdisjoint(s_two)
