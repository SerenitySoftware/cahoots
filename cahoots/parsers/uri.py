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
from cahoots.util import strings_intersect
import string
import socket
try:  # pragma: no cover
    # This is for Python 2 & 3 support.
    # pylint: disable=no-name-in-module
    from urllib.parse import urlparse
except ImportError:  # pragma: no cover
    # pylint: disable=import-error
    from urlparse import urlparse


class URIParser(BaseParser):
    """Determines if given data is a URI of some form"""

    def __init__(self, config):
        BaseParser.__init__(self, config, "URI", 100)

    @classmethod
    def is_ipv6_address(cls, address):
        """Checks if the data is an ipv6 address"""
        try:
            socket.inet_pton(socket.AF_INET6, address)
            return True
        except (socket.error, UnicodeEncodeError):
            pass

        return False

    @classmethod
    def is_ipv4_address(cls, address):
        """checks if the data is an ipv4 address"""
        try:
            socket.inet_aton(address)
            return True
        except (socket.error, UnicodeEncodeError):
            pass

        return False

    @classmethod
    def is_valid_url(cls, url):
        """Tries to parse a URL to see if it's valid"""
        pieces = urlparse(url)

        if not all([pieces.scheme, pieces.netloc]):
            return False

        if not set(pieces.netloc) <=\
                set(string.ascii_letters + string.digits + '-.'):
            return False

        return True

    def parse(self, data_string):
        if len(data_string) < 4:
            return

        dot_count = data_string.count(".")

        if dot_count >= 2 or data_string.count(":") >= 2:
            if self.is_ipv4_address(data_string):
                # lowering the confidence because "Technically"
                # an ipv4 address could be a phone number
                self.confidence -= 5
                # if there's whitespace in the ip address, lower confidence
                if strings_intersect(string.whitespace, data_string):
                    self.confidence -= 50
                yield self.result("IP Address (v4)")

            elif self.is_ipv6_address(data_string):
                yield self.result("IP Address (v6)")

        letters = [c for c in data_string if c in string.ascii_letters]

        if dot_count > 0 and len(letters) >= 4:
            if self.is_valid_url(data_string):
                yield self.result("URL")

            elif '://' not in data_string:
                if self.is_valid_url('http://' + data_string):
                    # confidence hit since we had to modify the data
                    self.confidence -= 25
                    yield self.result("URL", data='http://'+data_string)
