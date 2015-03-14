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
from cahoots.parsers.location import LocationDatabase, StreetSuffixEntity
from SereneRegistry import registry
import re
import sqlite3


class AddressParser(BaseParser):
    """Determines if given data is an address"""

    def __init__(self, config):
        BaseParser.__init__(self, config, "Address", 100)

    @staticmethod
    def bootstrap(config):
        """preps the address parser"""
        split_regex = re.compile("[\s`'?.;,-/]")
        registry.set('AP_split_regex', split_regex)

    @classmethod
    def get_street_suffix(cls, working_data):

        ldb = LocationDatabase()

        sqlItems = []

        for _ in working_data:
            sqlItems.append('suffix_name = ?')

        database = LocationDatabase.get_database()
        cursor = database.cursor()

        try:
            rows = cursor.execute(
                'SELECT * FROM street_suffix WHERE ' + " or ".join(sqlItems),
                tuple(working_data)
            ).fetchone()
            entities = LocationDatabase.hydrate([rows], StreetSuffixEntity)
        except sqlite3.Error:
            pass

        return entities or None

    def parse(self, data):
        """parses for address"""

        if len(data) > 75:
            return

        split_regex = registry.get('AP_split_regex')
        # splitting the data string and removing empty values
        working_data = [x for x in split_regex.split(data) if x]

        if len(working_data) <= 3:
            return

        suffix = self.get_street_suffix(working_data)
        if not suffix:
            return

        for suf in suffix:
            print vars(suf)

        # Going through the data backwards looking for a street suffix
        #for bit in reversed(working_data):
        #    pass
