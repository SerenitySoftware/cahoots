# coding: utf-8
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
# pylint: disable=anomalous-backslash-in-string
from cahoots.parsers.base import BaseParser
from SereneRegistry import registry
from LatLon import string2latlon, LatLon
import re


class CoordinateParser(BaseParser):
    """Detects if the data provided is a coordinate"""

    def __init__(self, config):
        BaseParser.__init__(self, config, "Coordinates", 100)

    @staticmethod
    def bootstrap(config):
        """Bootstraps the coordinate parser"""
        # Will test if something matches regular coordinates
        # 34.56,23.65 or 34.56 23.65 or 34.56 , 23.65
        coord_regex = re.compile(
            r'^(-?\d{1,3}(?:\.\d+)?)' +
            r'(?:(?:(?:\s+)?,(?:\s+)?)|(?:\s+))' +
            r'(-?\d{1,3}(?:\.\d+))?$'
        )
        registry.set('CP_coord_regex', coord_regex)

        # Will test if something matches degree coordinates
        # 40.244° N 79.123° W
        deg_regex = re.compile(
            u'^(\d{1,3}\.\d+°?\s+[nNsS])' +
            u'\s+' +
            u'(\d{1,3}\.\d+°?\s+[wWeE])$'
        )
        registry.set('CP_deg_regex', deg_regex)

        # Will test if something matches deg/min coordinates
        # 13° 34.425' N 45° 37.983' W
        deg_min_regex = re.compile(
            u'^(\d{1,3}°?\s+\d{1,3}\.\d+\'?\s+[nNsS])' +
            u'\s+' +
            u'(\d{1,3}°?\s+\d{1,3}\.\d+\'?\s+[wWeE])$'
        )
        registry.set('CP_deg_min_regex', deg_min_regex)

        # Will test if something matches deg/min/sec coordinates
        # 40° 26' 46.56" N 79° 58' 56.88" W
        deg_min_sec_regex = re.compile(
            u'^(\d{1,3}°?\s+\d{1,3}\'?\s+\d{1,3}(?:\.\d+)?"?\s+[nNsS])' +
            u'\s+' +
            u'(\d{1,3}°?\s+\d{1,3}\'?\s+\d{1,3}(?:\.\d+)?"?\s+[wWeE])$'
        )
        registry.set('CP_deg_min_sec_regex', deg_min_sec_regex)

    @classmethod
    def clean_dms_coords(cls, coord_string):
        """Removes items that the LatLon parser doesn't want"""
        coord_string = coord_string.replace(u'°', '')
        coord_string = coord_string.replace('\'', '')
        coord_string = coord_string.replace('"', '')
        return coord_string

    @classmethod
    def get_standard_coord_data(cls, match):
        """Creates LatLon from regular coords"""
        lat_lon = LatLon(
            float(match.group(1)),
            float(match.group(2))
        )
        return lat_lon

    def get_degree_based_coord_data(self, match, pattern):
        """Takes degree based coords and turns them into LatLon object"""
        lat_lon = string2latlon(
            self.clean_dms_coords(match.group(1)),
            self.clean_dms_coords(match.group(2)),
            pattern
        )
        return lat_lon

    @classmethod
    def generate_result_data(cls, result):
        """Adds a google map link to the result data"""
        result_dict = {
            'latitude': result[0],
            'longitude': result[1]
        }

        # throwing this in there for funsies
        url = 'https://www.google.com/maps?q=' + result[0] + ',' + result[1]
        additional_data = {
            'map_url': url
        }

        return result_dict, additional_data

    def get_coordinate_test_parameters(self):
        """Returns the test parameters for coordinate tests"""
        return [
            (
                # Standard coordinate match
                'CP_coord_regex',  # Name of the registry key holding regex
                self.get_standard_coord_data,  # formatting function
                None,  # Specific input format for the formatting function
                'Standard',  # Subtype if match
                80,  # Confidence if match
            ),
            (
                # Degree coordinate match
                'CP_deg_regex',
                self.get_degree_based_coord_data,
                'd% %H',
                'Degree',
                100,
            ),
            (
                # Degree/minute coordinate match
                'CP_deg_min_regex',
                self.get_degree_based_coord_data,
                'd% %m% %H',
                'Degree/Minute',
                100,
            ),
            (
                # Degree/minutes/second coordinate match
                'CP_deg_min_sec_regex',
                self.get_degree_based_coord_data,
                'd% %m% %S% %H',
                'Degree/Minute/Second',
                100,
            ),
        ]

    def parse(self, data):
        """parses data to determine if this is a location"""
        data = data.strip()

        test_parameters = self.get_coordinate_test_parameters()

        for reg_key, format_func, fmt, subtype, confidence in test_parameters:
            # checking each of our types of coordinates and breaking on find
            match = registry.get(reg_key).match(data)
            if match:
                # if a format_arg provided, we pass it into formatting func
                res = format_func(match, fmt) if fmt else format_func(match)

                # Prepping processed data with better metadata
                result, add_data = self.generate_result_data(res.to_string())
                yield self.result(subtype, confidence, result, add_data)

                # Only looking to match one format, so we break here
                break
