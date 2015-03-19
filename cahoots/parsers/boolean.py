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
from cahoots.parsers.base import BaseParser


class BooleanParser(BaseParser):
    '''Determines if given data is a boolean value'''

    strongTrue = ["true", "yes"]
    mediumTrue = ["yep", "yup"]
    weakTrue = ["1", "t", "one"]

    strongFalse = ["false", "no"]
    mediumFalse = ["nope"]
    weakFalse = ["0", "f", "zero"]

    def __init__(self, config):
        BaseParser.__init__(self, config, "Boolean")

    @classmethod
    def is_true(cls, data):
        """Checks if a value is true"""
        if data in cls.strongTrue:
            return 100
        elif data in cls.mediumTrue:
            return 75
        elif data in cls.weakTrue:
            return 50
        return 0

    @classmethod
    def is_false(cls, data):
        """Checks if a value is false"""
        if data in cls.strongFalse:
            return 100
        elif data in cls.mediumFalse:
            return 75
        elif data in cls.weakFalse:
            return 50
        return 0

    def parse(self, data):
        data = data.lower()

        # The largest boolean "value" we have is 5 characters long.
        if len(data) > 5:
            return

        # Testing for true
        confidence = self.is_true(data)
        if confidence:
            yield self.result("True", confidence, True)

        # Testing for false
        confidence = self.is_false(data)
        if confidence:
            yield self.result("False", confidence, False)
