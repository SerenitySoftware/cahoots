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

    def parse(self, data, **kwargs):
        """parses data to determine if this is a location"""
        data = data.strip()

        # Standard coordinate match
        match = registry.get('CP_coord_regex').match(data)
        if match:
            res = self.get_standard_coord_data(match)
            yield self.result("Standard", 80, res.to_string())
            return

        # Degree coordinate match
        match = registry.get('CP_deg_regex').match(data)
        if match:
            res = self.get_degree_based_coord_data(match, 'd% %H')
            yield self.result("Degree", 100, res.to_string())
            return

        # Degree/minute coordinate match
        match = registry.get('CP_deg_min_regex').match(data)
        if match:
            res = self.get_degree_based_coord_data(match, 'd% %m% %H')
            yield self.result("Degree/Minute", 100, res.to_string())
            return

        # Degree/minutes/second coordinate match
        match = registry.get('CP_deg_min_sec_regex').match(data)
        if match:
            res = self.get_degree_based_coord_data(match, 'd% %m% %S% %H')
            yield self.result("Degree/Minute/Second", 100, res.to_string())
            return
