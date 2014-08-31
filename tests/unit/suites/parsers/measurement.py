from cahoots.parsers.measurement import MeasurementParser
from tests.unit.config import TestConfig
from SereneRegistry import registry
import unittest


class MeasurementParserTests(unittest.TestCase):
    """Unit Testing of the MeasurementParser"""

    mp = None

    def setUp(self):
        MeasurementParser.bootstrap(TestConfig())
        self.mp = MeasurementParser(TestConfig())

    def tearDown(self):
        self.mp = None

    def test_loadUnits(self):
        self.assertTrue(registry.test('MPallUnits'))
        self.assertTrue(registry.test('MPsystemUnits'))

    def test_basicUnitCheck(self):
        self.assertTrue(self.mp.basicUnitCheck('parsec'))
        self.assertFalse(self.mp.basicUnitCheck('heffalump'))

    def test_determineSystemUnit(self):
        self.assertEqual(
            self.mp.determineSystemUnit('inches'),
            'imperial_length'
        )
        self.assertEqual(
            self.mp.determineSystemUnit('parsecs'),
            'miscellaneous_length'
        )
        self.assertIsNone(self.mp.determineSystemUnit('asdfasdf'))

    def test_identifyUnitsInData(self):
        data, matches = self.mp.identifyUnitsInData('3 square feet')
        self.assertEqual(data, '3')
        self.assertEqual(matches, ['square feet'])

        self.assertRaises(
            Exception,
            self.mp.identifyUnitsInData,
            '3 feet feet'
        )

    def test_getSubType(self):
        self.assertEqual(
            self.mp.getSubType('imperial_length'),
            'Imperial Length'
        )
        self.assertEqual(
            self.mp.getSubType('miscellaneous_length'),
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
            self.assertEqual(result.Confidence, 50)
            self.assertEqual(result.Subtype, 'Imperial Length')
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
            self.assertEqual(result.Confidence, 100)
            self.assertEqual(result.Subtype, 'Imperial Length')
            count += 1
        self.assertEqual(count, 1)

    def test_parseWithUnitButNoNumberYieldsExpectedConfidence(self):
        count = 0
        for result in self.mp.parse('snarf inches'):
            self.assertEqual(result.Confidence, 31)
            self.assertEqual(result.Subtype, 'Imperial Length')
            count += 1
        self.assertEqual(count, 1)

    def test_parseWithMultipleUnitTypesYieldsProperSubtype(self):
        count = 0
        for result in self.mp.parse('4 inches 50 liters'):
            self.assertEqual(result.Confidence, 34)
            self.assertEqual(result.Subtype, 'Imperial Length, Metric Volume')
            count += 1
        self.assertEqual(count, 1)

    def test_parseWithUnitButTooManyNonNumbersYieldsNothing(self):
        count = 0
        for result in self.mp.parse('foo bar biz baz inches'):
            count += 1
        self.assertEqual(count, 0)
