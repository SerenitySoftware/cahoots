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
from SereneRegistry import registry
from validate_email import VALID_ADDRESS_REGEXP
import re


class EmailParser(BaseParser):
    '''Determines if given data is an email address'''

    def __init__(self, config):
        BaseParser.__init__(self, config, "Email", 100)

    @staticmethod
    def bootstrap(config):
        """Bootstraps the email parser"""
        email_regex = re.compile(VALID_ADDRESS_REGEXP)
        registry.set('EP_valid_regex', email_regex)

    def parse(self, data_string):
        if len(data_string) > 254 or '@' not in data_string:
            return

        if registry.get('EP_valid_regex').match(data_string):
            yield self.result("Email Address", self.confidence)
