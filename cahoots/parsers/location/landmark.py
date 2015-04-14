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
        """
        :param config: cahoots config
        :type config: cahoots.config.BaseConfig
        """
        BaseParser.__init__(self, config, "Landmark", 100)

    @staticmethod
    def bootstrap(config):
        """
        This method is statically called to bootstrap a parser

        :param config: cahoots config
        :type config: cahoots.config.BaseConfig
        """
        the_regex = re.compile('^the ', re.IGNORECASE)
        registry.set('LP_the_regex', the_regex)

    @classmethod
    def find_matching_landmarks(cls, data):
        """
        Looks in the database for landmarks matching datastring

        :param data: string we want to check against landmarks
        :type data: str
        :return: list of landmarks
        :rtype: list
        """
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

    def prepare_landmark_datastring(self, data):
        """
        Cleans up and validates the datastring

        :param data: data we want to check for being a location
        :type data: str
        :return: the cleaned up datastring
        :rtype: str
        """
        data = registry.get('LP_the_regex').sub('', data).strip()

        if len(data) > 75:
            return

        name_parser = NameParser(self.config)
        if not name_parser.basic_validation(data.split()):
            return

        allowed_chars = \
            string.whitespace + string.ascii_letters + string.digits
        allowed_chars += '.,-:'

        if [x for x in data if x not in allowed_chars]:
            return

        return data

    def parse(self, data):
        """
        parses for landmarks

        :param data: the string we want to parse
        :type data: str
        :return: yields parse result(s) if there are any
        :rtype: ParseResult
        """
        data = self.prepare_landmark_datastring(data)

        if not data:
            return

        entities = self.find_matching_landmarks(data)

        if entities:
            self.confidence = \
                95-(2*len(entities)) if len(entities) > 1 else 95
            subtype = 'Single' if len(entities) == 1 else 'Multiple'
            yield self.result(subtype, self.confidence, entities)
