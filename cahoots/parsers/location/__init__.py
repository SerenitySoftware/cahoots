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
from SereneRegistry import registry
import sqlite3
import os


class LocationDatabase(object):
    """Handles the database for location parsing in various submodules"""

    @classmethod
    def get_database_cursor(cls):
        """Gets a sqlite database cursor for the location database"""

        if not registry.test('L_database'):
            data_dir = os.path.dirname(os.path.realpath(__file__))
            database = sqlite3.connect(data_dir + '/data/location.sqlite')
            database.cursor().execute('PRAGMA temp_store = 2')
            registry.set('L_database', database)
        else:
            database = registry.get('L_database')

        return database.cursor()

    def select(self, sql, params, entity):
        """Executes a statement (assumed to be a select) against the db"""
        if not isinstance(params, tuple):
            raise TypeError(
                'LocationDatabase.select requires params to be a tuple.'
            )

        cursor = self.get_database_cursor()
        rows = cursor.execute(sql, params).fetchall()

        if len(rows) > 0:
            entities = []
            for row in rows:
                entities.append(entity(row))
            return entities
        else:
            return None


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


class CountryEntity(object):
    """Represents a country database entity"""

    def __init__(self, data):
        self.abbreviation,\
            self.name = data
