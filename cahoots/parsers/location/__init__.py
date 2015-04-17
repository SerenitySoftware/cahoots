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
        """
        Gets a sqlite database connection to the location database

        :return: sqlite3 connection
        :rtype: _sqlite3.Connection
        """
        data_dir = os.path.dirname(os.path.realpath(__file__))
        database = sqlite3.connect(data_dir + '/data/location.sqlite')
        database.cursor().execute('PRAGMA temp_store = 2')
        return database

    def single_select(self, sql, params, prototype):
        """
        Executes a statement (assumed to be a select) against the db

        :param sql: the sql select that we want to execute
        :type sql: str
        :param params: the sql parameters to inject into the provided sql
        :type params: tuple
        :param prototype: The class we want to hydrate with results
        :type prototype: mixed
        :return: the hydrated prototype
        :rtype: mixed
        """
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
        """
        hydrates a set of entities

        :param data: the data retrieved from a select
        :type data: tuple
        :param prototype: the class we want to hydrate with the data
        :type prototype: mixed
        :return: hydrated prototype
        :rtype: mixed
        """
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
        """
        Preps our entity objects with country data and converts dicts

        :param entities: list of city entities to map country data to
        :type entities: list
        :param cursor: sqlite3 database cursor
        :type cursor: _sqlite3.Cursor
        :return: list of results with subbed country data
        :rtype: list
        """
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
        """
        :param data: data we want to hydrate this entity with
        :type data: tuple
        """
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
        """
        :param data: data we want to hydrate this entity with
        :type data: tuple
        """
        self.resource,\
            self.address,\
            self.city,\
            self.county,\
            self.state,\
            self.country = data


class CountryEntity(object):
    """Represents a country database entity"""

    def __init__(self, data):
        """
        :param data: data we want to hydrate this entity with
        :type data: tuple
        """
        self.abbreviation,\
            self.name = data


class StreetSuffixEntity(object):
    """Represents a street suffix entity"""

    def __init__(self, data):
        """
        :param data: data we want to hydrate this entity with
        :type data: tuple
        """
        self.suffix_name = data[0]
