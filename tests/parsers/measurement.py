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
from cahoots.data import DataHandler
from cahoots.parsers.measurement import MeasurementParser
from tests.config import TestConfig
from SereneRegistry import registry
import pyparsing
import unittest
import mock
import sys


if sys.version_info[0] < 3:
    BUILTINS_NAME = '__builtin__.open'
else:
    BUILTINS_NAME = 'builtins.open'


# pylint: disable=unused-argument
def mock_miscTextReturnSingleParameter(param1):
    return 'foo'


# pylint: disable=unused-argument
def mock_miscTextReturnDoubleParameter(param1, param2):
    return 'foo'


# pylint: disable=unused-argument
def mock_globGlob(path):
    return ['foo', 'bar']


# pylint: disable=unused-argument
def mock_open(filename, mode):
    if filename == 'foo':
        contents = ("system: Imperial\n"
                    "type: Area\n"
                    "id: imperial_area\n"
                    "keywords:\n"
                    "- acre\n"
                    "- acres")
        return contents
    elif filename == 'bar':
        contents = ("system: Imperial\n"
                    "type: Length\n"
                    "id: imperial_length\n"
                    "keywords:\n"
                    "- yard\n"
                    "- yards")
        return contents
    else:
        raise Exception("Invalid File Name: " + mode)


class MeasurementParserTests(unittest.TestCase):
    """Unit Testing of the MeasurementParser"""

    mp = None

    def setUp(self):
        MeasurementParser.bootstrap(TestConfig())
        self.mp = MeasurementParser(TestConfig())

    def tearDown(self):
        registry.flush()
        self.mp = None

    @mock.patch('os.path.dirname', mock_miscTextReturnSingleParameter)
    @mock.patch('os.path.abspath', mock_miscTextReturnSingleParameter)
    @mock.patch('os.path.join', mock_miscTextReturnDoubleParameter)
    @mock.patch('glob.glob', mock_globGlob)
    @mock.patch(BUILTINS_NAME, mock_open)
    @mock.patch.object(DataHandler, 'get_prepositions')
    def test_bootStrap(self, get_prepositions_mock):
        get_prepositions_mock.return_value = ['of']
        MeasurementParser.bootstrap(TestConfig)
        self.assertEqual(
            {
                'acres': 'imperial_area',
                'yards': 'imperial_length',
                'yard': 'imperial_length',
                'acre': 'imperial_area'
            },
            registry.get('MP_units')
        )
        self.assertEqual(
            {
                'imperial_length': ('Imperial', 'Length'),
                'imperial_area': ('Imperial', 'Area')
            },
            registry.get('MP_systems')
        )
        self.assertIsInstance(
            registry.get('MP_preposition_parser'),
            pyparsing.And
        )
        self.assertIsInstance(
            registry.get('MP_measurement_parser'),
            pyparsing.And
        )
        get_prepositions_mock.assert_called_once_with()

    def test_parseBasicUnitYieldsProperResult(self):
        count = 0
        for result in self.mp.parse('inches'):
            self.assertEqual(result.confidence, 100)
            self.assertEqual(result.subtype, 'Imperial Length')
            self.assertEqual(result.result_value, {
                "amount": None,
                "unit": "inches",
                "subject": None
            })
            count += 1
        self.assertEqual(count, 1)

    def test_parseWithSubjectYieldsProperResult(self):
        count = 0
        for result in self.mp.parse('4 yards of fabric'):
            self.assertEqual(result.confidence, 100)
            self.assertEqual(result.subtype, 'Imperial Length')
            self.assertEqual(result.result_value, {
                "amount": "4",
                "unit": "yards",
                "subject": "fabric"
            })
            count += 1
        self.assertEqual(count, 1)

    def test_parseSimpleMeasurementYieldsExpectedConfidence(self):
        count = 0
        for result in self.mp.parse('4 inches'):
            self.assertEqual(result.confidence, 100)
            self.assertEqual(result.subtype, 'Imperial Length')
            self.assertEqual(result.result_value, {
                "amount": "4",
                "unit": "inches",
                "subject": None
            })
            count += 1
        self.assertEqual(count, 1)

    def test_parseWithMultipleUnitTypesYieldsProperSubtype(self):
        count = 0
        for result in self.mp.parse('6 inches and 50 liters of koolaid'):
            if count == 0:
                self.assertEqual(result.confidence, 100)
                self.assertEqual(result.subtype, 'Imperial Length')
                self.assertEqual(result.result_value, {
                    "amount": "6",
                    "unit": "inches",
                    "subject": None
                })
            elif count == 1:
                self.assertEqual(result.confidence, 95)
                self.assertEqual(result.subtype, 'Metric Volume')
                self.assertEqual(result.result_value, {
                    "amount": "50",
                    "unit": "liters",
                    "subject": "koolaid"
                })
            count += 1
        self.assertEqual(count, 2)
