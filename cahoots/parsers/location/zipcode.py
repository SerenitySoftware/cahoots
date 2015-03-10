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
import pyzipcode
import re


class ZipCodeParser(BaseParser):
    """Detects if the data provided is a location"""

    def __init__(self, config):
        BaseParser.__init__(self, config, "Zip Code", 100)

    @staticmethod
    def bootstrap(config):
        """Bootstraps the location parser"""
        zcdb = pyzipcode.ZipCodeDatabase()
        registry.set('ZCP_zip_code_database', zcdb)

        # Will test if something matches 5 or 9 digit zipcode pattern
        zip_regex = re.compile(r'^\d{5}(-\d{4})?$', re.VERBOSE)
        registry.set('ZCP_zip_code_regex', zip_regex)

    @classmethod
    def get_zip_code_data(cls, data):
        """If this looks like a zip code, we try to get its info"""
        if len(data) == 5:
            zip_code = data
        else:
            zip_code = data[:5]

        zcdb = registry.get('ZCP_zip_code_database')

        try:
            zip_data = zcdb[zip_code]
            return zip_data
        except IndexError:
            return None

    def parse(self, data, **kwargs):
        """parses data to determine if this is a location"""
        data = data.strip()

        zip_regex = registry.get('ZCP_zip_code_regex')
        if zip_regex.match(data):
            zip_data = self.get_zip_code_data(data)
            if zip_data is not None:
                # we can't really be fully certain this is a zipcode
                self.confidence -= len(data)
                yield self.result("Zip Code", self.confidence, vars(zip_data))
                return
