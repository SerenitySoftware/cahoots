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
from cahoots.parsers.measurement import MeasurementParser
from tests.config import TestConfig
from SereneRegistry import registry
import unittest
import mock


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
        raise Exception("Invalid File Names")


class MeasurementParserTests(unittest.TestCase):
    """Unit Testing of the MeasurementParser"""

    mp = None

    def setUp(self):
        MeasurementParser.bootstrap(TestConfig())
        self.mp = MeasurementParser(TestConfig())

    def tearDown(self):
        self.mp = None

    @mock.patch('os.path.dirname', mock_miscTextReturnSingleParameter)
    @mock.patch('os.path.abspath', mock_miscTextReturnSingleParameter)
    @mock.patch('os.path.join', mock_miscTextReturnDoubleParameter)
    @mock.patch('glob.glob', mock_globGlob)
    @mock.patch('__builtin__.open', mock_open)
    def test_bootStrap(self):
        MeasurementParser.bootstrap(TestConfig)
        self.assertEqual(
            ['acres', 'yards', 'yard', 'acre'],
            registry.get('MP_all_units')
        )
        self.assertEqual(
            {
                'imperial_length':
                    {'keywords': ['yards', 'yard'],
                     'type': 'Length',
                     'system': 'Imperial',
                     'id': 'imperial_length'},
                'imperial_area':
                    {'keywords': ['acres', 'acre'],
                     'type': 'Area',
                     'system': 'Imperial',
                     'id': 'imperial_area'}
            },
            registry.get('MP_system_units')
        )

    def test_loadUnits(self):
        self.assertTrue(registry.test('MP_all_units'))
        self.assertTrue(registry.test('MP_system_units'))

    def test_basic_unit_check(self):
        self.assertTrue(self.mp.basic_unit_check('parsec'))
        self.assertFalse(self.mp.basic_unit_check('heffalump'))

    def test_determine_system_unit(self):
        self.assertEqual(
            self.mp.determine_system_unit('inches'),
            'imperial_length'
        )
        self.assertEqual(
            self.mp.determine_system_unit('parsecs'),
            'miscellaneous_length'
        )
        self.assertIsNone(self.mp.determine_system_unit('asdfasdf'))

    def test_identify_units_in_data(self):
        data, matches = self.mp.identify_units_in_data('3 square feet')
        self.assertEqual(data, '3')
        self.assertEqual(matches, ['square feet'])
        self.assertRaises(
            StandardError,
            self.mp.identify_units_in_data,
            '3 feet feet'
        )
        self.assertRaises(
            StandardError,
            self.mp.identify_units_in_data,
            'Mount Rushmore'
        )

    def test_get_sub_type(self):
        self.assertEqual(
            self.mp.get_sub_type('imperial_length'),
            'Imperial Length'
        )
        self.assertEqual(
            self.mp.get_sub_type('miscellaneous_length'),
            'Miscellaneous Length'
        )

    def test_parseZeroLengthYieldNothing(self):
        count = 0
        for _ in self.mp.parse(' '):
            count += 1
        self.assertEqual(count, 0)

    def test_parseLongStringYieldsNothing(self):
        count = 0
        for _ in self.mp.parse(
                'hellohellohellohellohellohellohellohellohellohellohello'
        ):
            count += 1
        self.assertEqual(count, 0)

    def test_parseBasicUnitYieldsProperResult(self):
        count = 0
        for result in self.mp.parse('inches'):
            self.assertEqual(result.confidence, 50)
            self.assertEqual(result.subtype, 'Imperial Length')
            count += 1
        self.assertEqual(count, 1)

    def test_parseNoWhitespaceOrDigitsYieldsNothing(self):
        count = 0
        for _ in self.mp.parse('scoobydoo'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseDoubleUnitYieldsNothing(self):
        count = 0
        for _ in self.mp.parse('4 inches inches'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseLooksLikeMeasurementButNoUnitsYieldsNothing(self):
        count = 0
        for _ in self.mp.parse('4 lafawndas'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseSimpleMeasurementYieldsExpectedConfidence(self):
        count = 0
        for result in self.mp.parse('4 inches'):
            self.assertEqual(result.confidence, 100)
            self.assertEqual(result.subtype, 'Imperial Length')
            count += 1
        self.assertEqual(count, 1)

    def test_parseWithUnitButNoNumberYieldsExpectedConfidence(self):
        count = 0
        for result in self.mp.parse('snarf inches'):
            self.assertEqual(result.confidence, 31)
            self.assertEqual(result.subtype, 'Imperial Length')
            count += 1
        self.assertEqual(count, 1)

    def test_parseWithMultipleUnitTypesYieldsProperSubtype(self):

        expected_results = [
            [34, 'Imperial Length'],
            [34, 'Metric Volume']
        ]

        count = 0
        for result in self.mp.parse('4 inches 50 liters'):
            self.assertEqual(result.confidence, expected_results[count][0])
            self.assertEqual(result.subtype, expected_results[count][1])
            count += 1
        self.assertEqual(count, 2)

    def test_parseWithUnitButTooManyNonNumbersYieldsNothing(self):
        count = 0
        for _ in self.mp.parse('foo bar biz baz inches'):
            count += 1
        self.assertEqual(count, 0)
