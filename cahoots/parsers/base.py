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
from cahoots.result import ParseResult


class BaseParser(object):
    '''Base parser that other parsers should extend'''

    config = None
    type = "Base"
    confidence = 10

    def __init__(self, config, p_type="Base", confidence=10):
        self.config = config
        self.type = p_type
        self.confidence = confidence

    @staticmethod
    def bootstrap(config):
        '''This method can be statically called to bootstrap a parser'''
        pass

    def parse(self, data):
        """Base parse method"""
        raise NotImplementedError("Class must override the parse() method")

    def result(self, subtype="Unknown", confidence=0, value=None, data=None):
        """Returns a ParseResult object detailing the results of parsing"""
        if confidence == 0:
            confidence = self.confidence

        if data is None:
            data = {}

        return ParseResult(
            p_type=self.type,
            subtype=subtype,
            confidence=confidence,
            value=value,
            additional_data=data
        )
