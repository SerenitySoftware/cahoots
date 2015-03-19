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
# pylint: disable=invalid-name,too-many-public-methods,missing-docstring
from cahoots.parsers.location.coordinate import CoordinateParser
from tests.config import TestConfig
from SereneRegistry import registry
import unittest


class CoordinateParserTests(unittest.TestCase):
    """Unit testing of the coordinate parser"""

    cp = None

    def setUp(self):
        CoordinateParser.bootstrap(TestConfig())
        self.cp = CoordinateParser(TestConfig())

    def tearDown(self):
        registry.flush()
        self.cp = None

    def test_parseWithStandardCoordsYieldsExpectedResult(self):
        results = self.cp.parse('-23.5234, 56.7286')
        count = 0
        for result in results:
            count += 1
            self.assertEqual(result.subtype, 'Standard')
            self.assertEqual(
                result.result_value,
                {'latitude': '-23.5234', 'longitude': '56.7286'}
            )
            self.assertEqual(
                result.data,
                {'map_url': 'https://www.google.com/maps?q=-23.5234,56.7286'}
            )
            self.assertEqual(result.confidence, 80)
        self.assertEqual(1, count)

    def test_parseWithDegCoordsYieldsExpectedResult(self):
        results = self.cp.parse(u'40.244° N 79.123° W')
        count = 0
        for result in results:
            count += 1
            self.assertEqual(result.subtype, 'Degree')
            self.assertEqual(
                result.result_value,
                {'latitude': '40.244', 'longitude': '-79.123'}
            )
            self.assertEqual(
                result.data,
                {'map_url': 'https://www.google.com/maps?q=40.244,-79.123'}
            )
            self.assertEqual(result.confidence, 100)
        self.assertEqual(1, count)

    def test_parseWithDegMinCoordsYieldsExpectedResult(self):
        results = self.cp.parse(u'13° 34.425\' N 45° 37.983\' W')
        count = 0
        for result in results:
            count += 1
            self.assertEqual(result.subtype, 'Degree/Minute')
            self.assertEqual(
                result.result_value,
                {'latitude': '13.57375', 'longitude': '-45.63305'}
            )
            self.assertEqual(
                result.data,
                {
                    'map_url':
                        'https://www.google.com/maps?q=13.57375,-45.63305'
                }
            )
            self.assertEqual(result.confidence, 100)
        self.assertEqual(1, count)

    def test_parseWithDegMinSecCoordsYieldsExpectedResult(self):
        results = self.cp.parse(u'40° 26\' 46.56" N 79° 58\' 56.88" W')
        count = 0
        for result in results:
            count += 1
            self.assertEqual(result.subtype, 'Degree/Minute/Second')
            self.assertEqual(
                result.result_value,
                {'latitude': '40.4462666667', 'longitude': '-79.9824666667'}
            )
            self.assertEqual(
                result.data,
                {
                    'map_url': 'https://www.google.com/maps?' +
                               'q=40.4462666667,-79.9824666667'
                }
            )
            self.assertEqual(result.confidence, 100)
        self.assertEqual(1, count)
