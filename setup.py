# coding: utf-8
import csv
import sqlite3
import subprocess
from setuptools import setup
from setuptools.command.install import install
from distutils import log


class cahoots_install(install):
    """
    Extension of setuptools install class for post-install scripting
    """

    def prep_location_data(self):
        """Copies dist database and extracts location data"""
        location_install_cmds = [
            'cp {0}cahoots/parsers/location/data/location.sqlite.dist {0}cahoots/parsers/location/data/location.sqlite',
            'bzip2 -d -k {0}cahoots/parsers/location/data/city.txt.bz2',
            'bzip2 -d -k {0}cahoots/parsers/location/data/country.csv.bz2',
            'bzip2 -d -k {0}cahoots/parsers/location/data/street_suffix.csv.bz2',
            'bzip2 -d -k {0}cahoots/parsers/location/data/landmark.csv.bz2',
        ]

        for command in location_install_cmds:
            subprocess.call(command.format(self.install_lib), shell=True)

    def import_city_data(self, cursor):
        """Imports city data"""
        city_file = self.install_lib+'cahoots/parsers/location/data/city.txt'
        city_csv = csv.DictReader(
            open(city_file, 'rb'),
            delimiter='\t',
            quotechar='"',
            fieldnames=['country', 'postal_code', 'city', 'state1', 'state2', 'province1', 'province2', 'community1', 'community2', 'latitude', 'longitude', 'coord_accuracy']
        )
        cursor.executemany(
            "INSERT INTO city (country, postal_code, city, state1, state2, province1, province2, community1, community2, latitude, longitude, coord_accuracy) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
            [(i['country'], i['postal_code'], i['city'], i['state1'], i['state2'], i['province1'], i['province2'], i['community1'], i['community2'], i['latitude'], i['longitude'], i['coord_accuracy'])
             for i in city_csv]
        )

    def import_country_data(self, cursor):
        """Imports country data"""
        country_file = self.install_lib+'cahoots/parsers/location/data/country.csv'
        country_csv = csv.DictReader(
            open(country_file, 'rb'),
            delimiter=',',
            quotechar='"',
            fieldnames=['abbreviation', 'name']
        )
        cursor.executemany(
            "INSERT INTO country (abbreviation, name) VALUES (?, ?);",
            [(i['abbreviation'], i['name'])
             for i in country_csv]
        )

    def import_street_suffix_data(self, cursor):
        """Imports street_suffix data"""
        suffix_file = self.install_lib+'cahoots/parsers/location/data/street_suffix.csv'
        suffix_csv = csv.DictReader(
            open(suffix_file, 'rb'),
            delimiter=',',
            quotechar='"',
            fieldnames=['suffix_name']
        )
        cursor.executemany(
            "INSERT INTO street_suffix (suffix_name) VALUES (?);",
            [(i['suffix_name'],)
             for i in suffix_csv]
        )

    def import_landmark_data(self, cursor):
        """Imports landmark data"""
        landmark_file = self.install_lib+'cahoots/parsers/location/data/landmark.csv'
        landmark_csv = csv.DictReader(
            open(landmark_file, 'rb'),
            delimiter=',',
            quotechar='"',
            fieldnames=['resource', 'address', 'city', 'county', 'state', 'country']
        )
        cursor.executemany(
            "INSERT INTO landmark (resource, address, city, county, state, country) VALUES (?, ?, ?, ?, ?, ?);",
            [(i['resource'], i['address'], i['city'], i['county'], i['state'], i['country'])
             for i in landmark_csv]
        )

    def cleanup_location_data(self):
        """Deletes temp files"""
        location_cleanup_cmds = [
            'rm {0}cahoots/parsers/location/data/city.txt',
            'rm {0}cahoots/parsers/location/data/country.csv',
            'rm {0}cahoots/parsers/location/data/street_suffix.csv',
            'rm {0}cahoots/parsers/location/data/landmark.csv',
        ]

        for command in location_cleanup_cmds:
            subprocess.call(command.format(self.install_lib), shell=True)

    def run(self):
        """Runs the install and post-install actions"""
        install.run(self)

        log.info("Preparing/extracting location database and data for import...")
        self.prep_location_data()

        log.info("Importing location data into location database...")
        database = sqlite3.connect(self.install_lib+'cahoots/parsers/location/data/location.sqlite')
        database.text_factory = str
        cursor = database.cursor()

        log.info("Importing city data...")
        self.import_city_data(cursor)

        log.info("Importing country data...")
        self.import_country_data(cursor)

        log.info("Importing street suffix data...")
        self.import_street_suffix_data(cursor)

        log.info("Importing landmark data...")
        self.import_landmark_data(cursor)

        database.commit()
        database.close()

        log.info('Cleaning up location import temporary files...')
        self.cleanup_location_data()

        log.info('Done!')


setup (
    cmdclass = {
        'install': cahoots_install
    },
    name = 'Cahoots',
    version = '0.2.1',
    url = 'https://github.com/SerenitySoftwareLLC/cahoots',
    maintainer='Serenity Software',
    maintainer_email = 'hello@serenitysoftware.io',
    description = 'A Text Comprehension Engine in Python.',
    long_description = open('README.rst', 'r').read(),
    license = 'MIT',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires = [
        'watchdog',
        'flask',
        'mako',
        'dateutils',
        'pyyaml',
        'pygments',
        'pyparsing',
        'phonenumbers',
        'simplejson',
        'SereneRegistry',
        'LatLon',
        'simplebayes',
        'validate_email',
    ],
    packages = [
        'cahoots',
        'cahoots.confidence',
        'cahoots.confidence.normalizers',
        'cahoots.parsers',
        'cahoots.parsers.location',
        'cahoots.parsers.measurement',
        'cahoots.parsers.programming',
        'cahootserver',
    ],
    package_data = {
        'cahoots': [
            # Location
            'parsers/location/data/*.sql',
            'parsers/location/data/*.bz2',
            'parsers/location/data/location.sqlite.dist',
            'parsers/location/data/LICENSE',
            # Programming
            'parsers/programming/languages/*',
            'parsers/programming/LICENSES/*',
            'parsers/programming/trainers.zip',
            # Measurement
            'parsers/measurement/units/*',
        ],
        'cahootserver': [
            'static/*',
            'templates/*',
        ],
    },
    entry_points={
        'console_scripts': [
            'cahootserver = cahootserver.server:launch_server',
        ],
    },
)
# python ./setup.py sdist upload