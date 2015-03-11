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
from cahoots.parsers.location import \
    LocationDatabase, CityEntity, CountryEntity
import re


class ZipCodeParser(BaseParser):
    """Detects if the data provided is a location"""

    def __init__(self, config):
        BaseParser.__init__(self, config, "Zip Code", 100)

    @staticmethod
    def bootstrap(config):
        """Bootstraps the location parser"""
        # Will test if something matches 5 or 9 digit zipcode pattern
        zip_regex = re.compile(r'^\d{5}(-\d{4})?$', re.VERBOSE)
        registry.set('ZCP_zip_code_regex', zip_regex)

    def get_zip_code_data(self, data):
        """If this looks like a zip code, we try to get its info"""
        if len(data) == 5:
            zip_code = data
        else:
            zip_code = data[:5]

        ldb = LocationDatabase()
        entities = ldb.select(
            'SELECT * FROM city WHERE postal_code = ?',
            (zip_code,),
            CityEntity
        )

        if entities is not None:
            entities = self.prepare_zip_code_data(entities)

        return entities

    @classmethod
    def prepare_zip_code_data(cls, entities):
        """Preps our CityEntity objects with country data and converts dicts"""
        ldb = LocationDatabase()
        cities = []

        for city in entities:
            entities = ldb.select(
                'SELECT * FROM country WHERE abbreviation = ?',
                (city.country,),
                CountryEntity
            )

            if len(entities) > 0:
                entity = entities[0]
                entity.name = entity.name.title()
                entity.abbreviation = entity.abbreviation.upper()
                city.country = vars(entity)

            cities.append(vars(city))

        return cities

    def calculate_confidence(self, data, results):
        """calculates the confidence that this is a zip code"""

        # The longer the data string, the higher the confidence
        self.confidence -= (20-len(data))

        if len(results) > 1:
            self.confidence -= (3 * len(results))

    def parse(self, data, **kwargs):
        """parses data to determine if this is a location"""
        data = data.strip()

        if len(data) >= 20:
            return

        zip_regex = registry.get('ZCP_zip_code_regex')
        if zip_regex.match(data):
            results = self.get_zip_code_data(data)
            if results is not None:
                self.calculate_confidence(data, results)
                if len(data) == 5:
                    sub_type = 'Standard'
                else:
                    sub_type = 'Plus Four'
                yield self.result(sub_type, self.confidence, results)
                return
