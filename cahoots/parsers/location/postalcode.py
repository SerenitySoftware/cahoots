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


class PostalCodeParser(BaseParser):
    """Detects if the data provided is a location"""

    def __init__(self, config):
        BaseParser.__init__(self, config, "Postal Code", 100)

    @staticmethod
    def bootstrap(config):
        """Bootstraps the location parser"""
        # Will test if something matches 5 or 9 digit postalcode pattern
        postal_regex = re.compile(
            r'^' +
            r'(\d{2,7}(-\d{2,4})?)|' +
            r'([a-zA-Z]\d{3})|' +
            r'([a-zA-Z]{2}\s\d{2})|' +
            r'([a-zA-Z]{2}-\d{2})|' +
            r'(AD\d{3})|' +
            r'(\d{3}\s\d{2})|' +
            r'([a-zA-Z]{2}\d{4})|' +
            r'(\d{4}\sW3)|' +
            r'(\d{4}\s[a-zA-Z]{2})|' +
            r'([a-zA-Z]\d[a-zA-Z]\s\d[a-zA-Z]\d)|' +
            r'(AZ\s\d{4})|' +
            r'(BB\d{1,5})|' +
            r'([a-zA-Z]{2}\d{1,2}\s\d[a-zA-Z]{2})|' +
            r'(JMA[a-zA-Z]{2}\d{2})|' +
            r'(AZ-\d{4})|' +
            r'([a-zA-Z]\d{4}[a-zA-Z]{3})|' +
            r'([a-zA-Z]{2}\d{2}\s\d[a-zA-Z]{2})|' +
            r'([a-zA-Z]{3}\s\d{4})|' +
            r'([a-zA-Z]{4}\s1ZZ)|' +
            r'([a-zA-Z]{2}\d{1,2}(-\d{4})?)|' +
            r'(\d{5}\sCEDEX(\s\d{1,2})?)' +
            r'$'
        )
        registry.set('ZCP_postal_code_regex', postal_regex)

    def get_postal_code_data(self, data):
        """If this looks like a postal code, we try to get its info"""
        plus_postal_code = '-' in data

        if plus_postal_code:
            prefix = data.split('-')[0]

        ldb = LocationDatabase()

        entities = ldb.select(
            'SELECT * FROM city WHERE postal_code = ?',
            (data,),
            CityEntity
        )
        entities = entities or []

        if plus_postal_code:
            prefix_entities = ldb.select(
                'SELECT * FROM city WHERE postal_code = ?',
                (prefix,),
                CityEntity
            )
            prefix_entities = prefix_entities or []
            entities.extend(prefix_entities)

        if not entities:
            return None

        entities = self.prepare_postal_code_data(entities)

        return entities

    @classmethod
    def prepare_postal_code_data(cls, entities):
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
        """calculates the confidence that this is a postal code"""

        # The longer the data string, the higher the confidence
        self.confidence -= (20-len(data))

        if len(results) > 1:
            self.confidence -= (3 * len(results))

    def parse(self, data, **kwargs):
        """parses data to determine if this is a location"""
        data = data.strip()

        if len(data) >= 20:
            return

        postal_regex = registry.get('ZCP_postal_code_regex')
        if postal_regex.match(data):
            results = self.get_postal_code_data(data)
            if results is not None:
                self.calculate_confidence(data, results)
                yield self.result(None, self.confidence, results)
                return
