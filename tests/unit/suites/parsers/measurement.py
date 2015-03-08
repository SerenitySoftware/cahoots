from cahoots.parsers.measurement import MeasurementParser
from tests.unit.config import TestConfig
from SereneRegistry import registry
import unittest
import mock


class MeasurementParserTests(unittest.TestCase):
    """Unit Testing of the MeasurementParser"""

    mp = None

    def setUp(self):
        MeasurementParser.bootstrap(TestConfig())
        self.mp = MeasurementParser(TestConfig())

    def tearDown(self):
        self.mp = None

    def mock_miscTextReturnSingleParameter(param1):
        return 'foo'

    def mock_miscTextReturnDoubleParameter(param1, param2):
        return 'foo'

    def mock_globGlob(path):
        return ['foo', 'bar']

    def mock_open(file, mode):
        if file == 'foo':
            contents = ("system: Imperial\n"
                        "type: Area\n"
                        "id: imperial_area\n"
                        "keywords:\n"
                        "- acre\n"
                        "- acres")
            return contents
        elif file == 'bar':
            contents = ("system: Imperial\n"
                        "type: Length\n"
                        "id: imperial_length\n"
                        "keywords:\n"
                        "- yard\n"
                        "- yards")
            return contents
        else:
            raise Exception("Invalid File Names")

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
        self.assertEqual({
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
            }, registry.get('MP_system_units')
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
            Exception,
            self.mp.identify_units_in_data,
            '3 feet feet'
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
        for result in self.mp.parse(' '):
            count += 1
        self.assertEqual(count, 0)

    def test_parseLongStringYieldsNothing(self):
        count = 0
        for result in self.mp.parse(
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
        for result in self.mp.parse('scoobydoo'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseDoubleUnitYieldsNothing(self):
        count = 0
        for result in self.mp.parse('4 inches inches'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseLooksLikeMeasurementButNoUnitsYieldsNothing(self):
        count = 0
        for result in self.mp.parse('4 lafawndas'):
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
        count = 0
        for result in self.mp.parse('4 inches 50 liters'):
            self.assertEqual(result.confidence, 34)
            self.assertEqual(result.subtype, 'Imperial Length, Metric Volume')
            count += 1
        self.assertEqual(count, 1)

    def test_parseWithUnitButTooManyNonNumbersYieldsNothing(self):
        count = 0
        for result in self.mp.parse('foo bar biz baz inches'):
            count += 1
        self.assertEqual(count, 0)
