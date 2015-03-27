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
from cahoots.parsers.name import NameParser
from cahoots.parsers.location import \
    LocationDatabase, StreetSuffixEntity
from SereneRegistry import registry
import re
import sqlite3
import itertools


class AddressParser(BaseParser):
    """
    Determines if given data is an address

    We don't use regex to find addresses because it's pretty much
    impossible to match all the possible (infinite) combinations.

    Instead, we look for elements that addresses have, or don't have,
    and determine if it's likely that this is an address or not.
    """

    subtype = "Without Addressee"

    def __init__(self, config):
        BaseParser.__init__(self, config, "Address", 0)

    @staticmethod
    def bootstrap(config):
        """preps the address parser"""
        split_regex = re.compile(r"[\s#`'?.;,-/]")
        registry.set('AP_split_regex', split_regex)

    @classmethod
    def get_street_suffix(cls, data_set):
        """Looks at our data for a street suffix and returns the entity"""
        sql_items = []

        for _ in data_set:
            sql_items.append('suffix_name = ?')

        database = LocationDatabase.get_database()
        cursor = database.cursor()

        try:
            row = cursor.execute(
                'SELECT * FROM street_suffix WHERE ' + " or ".join(sql_items),
                tuple(data_set)
            ).fetchone()
            database.close()
        except sqlite3.Error:
            database.close()
            return None

        if row is not None:
            return LocationDatabase.hydrate(row, StreetSuffixEntity)

    @classmethod
    def separate_suspected_name(cls, data_set):
        """Separates a suspected name from the beginning of an address"""
        name_elems = []
        work_data = list(data_set)
        conjunctions = ['and', 'but', 'or', 'yet', 'for', 'nor', 'so']
        for word in data_set:
            if not word[0].isdigit():
                work_data.pop(0)
                # skipping conjunctions, ex: Alice and Bob Saget
                if word.lower() not in conjunctions:
                    name_elems.append(word)
            else:
                break

        return (list(work_data), " ".join(name_elems))

    def is_address_name(self, suspected_name):
        """Checking if the start of an address bears a name"""
        name_parser = NameParser(self.config)
        for _ in name_parser.parse(suspected_name):
            return True
        return False

    @classmethod
    def is_invalid_int(cls, word):
        """Looking for ints that are to short (less than 5 chars)"""
        try:
            int(word)
            if len(word) < 5:
                return True
            else:
                return False
        except ValueError:
            return False

    def find_address_tokens(self, data, results):
        """Looking for known city or country, zip, etc."""
        tokens = 0
        working_data = list(data)

        data_combinations = list(itertools.combinations(working_data, 2))
        data_combinations = [" ".join(x) for x in data_combinations]

        working_data.extend(data_combinations)

        database = LocationDatabase.get_database()
        cursor = database.cursor()

        for test in [x for x in working_data if not self.is_invalid_int(x)]:

            params = (test, test, test, test, test)

            sql = 'SELECT count(*) FROM city WHERE ' +\
                  'country = ? OR ' +\
                  'postal_code = ? OR ' +\
                  'city = ? OR ' +\
                  'state1 = ? OR ' +\
                  'state2 = ?'

            try:
                row = cursor.execute(sql, params).fetchone()
                row = row[0]
            except sqlite3.Error:
                database.close()
                return 0, results

            if row:
                entity = {}
                entity['token'] = test
                entity['matches'] = row
                results['address_tokens'].append(entity)
                tokens += 1
                self.confidence += 20

        database.close()

        return (tokens, results)

    def generate_result_data(self, data, data_set):
        """
        Examines the data_set and generates a result
        dict, or returns nothing if there's a failure
        """
        results = {
            'street_suffix': None,
            'addressed_to': None,
            'address_tokens': []
        }

        # With no street suffix, we don't consider this an address
        suffix = self.get_street_suffix(data_set)
        if not suffix:
            return

        suffix_test = [x.lower() for x in data_set]
        try:
            # removing the suffix from the list of working data
            index = suffix_test.index(suffix.suffix_name)
            data_set.pop(index)
        except ValueError:
            # if for some reason we found an invalid suffix, we probably cry
            return

        results['street_suffix'] = suffix.suffix_name

        # Looking to see if this address starts with a name, since no digit
        if not data[0].isdigit():
            data_set, suspected_name = \
                self.separate_suspected_name(data_set)

            results['addressed_to'] = suspected_name

            if NameParser in self.config.enabled_modules:
                if self.is_address_name(suspected_name):
                    self.subtype = "With Addressee"
                    self.confidence += 25
                else:
                    # If it starts with non-name text, not an address
                    return

        # Looking for items in the city database that match words in the data
        token_count, results = self.find_address_tokens(data_set, results)

        return (results, token_count, data_set)

    def parse(self, data):
        """parses for address"""
        data = data.strip()

        # If invalid length or there are no digits, we return.
        if len(data) > 100 or not [x for x in data if x.isdigit()]:
            return

        split_regex = registry.get('AP_split_regex')
        # splitting the data string and removing empty values
        data_set = [x for x in split_regex.split(data) if x]

        # At least 4 words and one of the words should start with a number
        if len(data_set) <= 3 or not [x for x in data_set if x[:1].isdigit()]:
            return

        results, token_count, data_set = \
            self.generate_result_data(data, data_set) \
            or (None, None, None)

        if token_count:
            # Subtracting a little confidence for each token that wasn't found
            self.confidence -= 5*(len(data_set)-token_count)

            yield self.result(self.subtype, min(100, self.confidence), results)
