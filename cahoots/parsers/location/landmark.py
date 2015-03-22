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
from cahoots.parsers.location import LocationDatabase, LandmarkEntity
from cahoots.parsers.name import NameParser
from SereneRegistry import registry
import sqlite3
import string
import re


class LandmarkParser(BaseParser):
    """
    Determines if given data is a landmark

    This is dependent on if the landmark is in our database of landmarks.
    """

    def __init__(self, config):
        BaseParser.__init__(self, config, "Landmark", 100)

    @staticmethod
    def bootstrap(config):
        """preps the address parser"""
        the_regex = re.compile('^the ', re.IGNORECASE)
        registry.set('LP_the_regex', the_regex)

    @classmethod
    def find_matching_landmarks(cls, data):
        """Looks in the database for landmarks matching datastring"""
        database = LocationDatabase.get_database()
        cursor = database.cursor()

        try:
            rows = cursor.execute(
                'SELECT * FROM landmark WHERE resource like ?',
                (data + '%',)
            ).fetchall()
            entities = LocationDatabase.hydrate(rows, LandmarkEntity)
            entities = \
                LocationDatabase.substitute_country_data(entities, cursor)
            entities = [vars(x) for x in entities]
            database.close()
        except sqlite3.Error:
            database.close()
            return

        return entities

    @classmethod
    def prepare_landmark_datastring(cls, data):
        """Cleans up and validates the datastring"""
        data = registry.get('LP_the_regex').sub('', data).strip()

        if len(data) > 75:
            return

        if not NameParser.basic_validation(data.split()):
            return

        allowed_chars = string.whitespace + string.letters + string.digits
        allowed_chars += '.,-:'

        if [x for x in data if x not in allowed_chars]:
            return

        return data

    def parse(self, data):
        """parses for landmarks"""
        data = self.prepare_landmark_datastring(data)

        if not data:
            return

        entities = self.find_matching_landmarks(data)

        if entities:
            self.confidence = \
                95-(2*len(entities)) if len(entities) > 1 else 95
            subtype = 'Single' if len(entities) == 1 else 'Multiple'
            yield self.result(subtype, self.confidence, entities)
