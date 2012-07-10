from brain.parsers.measurement import MeasurementParser
from brain.util import BrainRegistry
import unittest

class MeasurementParserTests(unittest.TestCase):
    """Unit Testing of the MeasurementParser"""

    mp = None

    def setUp(self):
        self.mp = MeasurementParser()

    def tearDown(self):
        self.mp = None


    def test_loadUnits(self):

        # if we have units in the registry, we know the loadunits method worked,
        # because it's the only way they get loaded
        self.assertTrue(BrainRegistry.test('MPallUnits'))
        self.assertTrue(BrainRegistry.test('MPsystemUnits'))


    def test_basicUnitCheck(self):

        self.assertTrue(self.mp.basicUnitCheck('parsec'))
        
        self.assertFalse(self.mp.basicUnitCheck('heffalump'))
        

    def test_determineSystemUnit(self):

        self.assertEqual(self.mp.determineSystemUnit('inches'), 'imperial_length')
        self.assertEqual(self.mp.determineSystemUnit('parsecs'), 'miscellaneous_length')

        self.assertIsNone(self.mp.determineSystemUnit('asdfasdf'))


    def test_identifyUnitsInData(self):

        data, matches = self.mp.identifyUnitsInData('3 square feet')

        self.assertEqual(data, '3')
        self.assertEqual(matches, ['square feet'])


    def test_getSubType(self):

        self.assertEqual(self.mp.getSubType('imperial_length'), 'Imperial Length')
        self.assertEqual(self.mp.getSubType('miscellaneous_length'), 'Miscellaneous Length')