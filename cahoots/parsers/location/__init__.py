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
import sqlite3
import os


class LocationDatabase(object):
    """Handles the database for location parsing in various submodules"""

    @classmethod
    def get_database(cls):
        """Gets a sqlite database connection to the location database"""
        data_dir = os.path.dirname(os.path.realpath(__file__))
        database = sqlite3.connect(data_dir + '/data/location.sqlite')
        database.cursor().execute('PRAGMA temp_store = 2')
        return database

    def single_select(self, sql, params, prototype):
        """Executes a statement (assumed to be a select) against the db"""
        if not isinstance(params, tuple):
            raise TypeError(
                'LocationDatabase.select requires params to be a tuple.'
            )

        database = self.get_database()
        cursor = database.cursor()

        try:
            rows = cursor.execute(sql, params).fetchall()
        except sqlite3.Error:
            database.close()
            return None

        database.close()

        if len(rows) > 0:
            return self.hydrate(rows, prototype)
        else:
            return None

    @classmethod
    def hydrate(cls, data, prototype):
        """hydrates a set of entities"""
        if isinstance(data, list):
            entities = []
            for row in data:
                entities.append(prototype(row))
            return entities
        elif isinstance(data, tuple):
            return prototype(data)
        else:
            raise TypeError(
                'Location entity hydration requires a list or tuple.'
            )

    @classmethod
    def substitute_country_data(cls, entities, cursor):
        """Preps our entity objects with country data and converts dicts"""
        results = []

        for result in entities:
            try:
                rows = cursor.execute(
                    'SELECT * FROM country WHERE abbreviation = ?',
                    (result.country,)
                ).fetchall()
            except sqlite3.Error:
                rows = []

            if rows:
                entities = LocationDatabase.hydrate(rows, CountryEntity)
                entity = entities[0]
                entity.name = entity.name.title()
                entity.abbreviation = entity.abbreviation.upper()
                result.country = vars(entity)

            results.append(result)

        return results


# pylint: disable=too-many-instance-attributes
class CityEntity(object):
    """Represents a city database entity"""

    def __init__(self, data):
        self.country,\
            self.postal_code,\
            self.city,\
            self.state1,\
            self.state2,\
            self.province1,\
            self.province2,\
            self.community1,\
            self.community2,\
            self.latitude,\
            self.longitude,\
            self.coord_accuracy = data


class LandmarkEntity(object):
    """Represents a landmark database entity"""

    def __init__(self, data):
        self.resource,\
            self.address,\
            self.city,\
            self.county,\
            self.state,\
            self.country = data


class CountryEntity(object):
    """Represents a country database entity"""

    def __init__(self, data):
        self.abbreviation,\
            self.name = data


class StreetSuffixEntity(object):
    """Represents a street suffix entity"""

    def __init__(self, data):
        self.suffix_name = data[0]
