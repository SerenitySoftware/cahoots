from cahoots.parsers.name import NameParser
from tests.unit.config import TestConfig
import unittest

class NameParserTests(unittest.TestCase):
    """Unit Testing of the NameParser"""

    np = None

    def setUp(self):
        self.np = NameParser(TestConfig())

    def tearDown(self):
        self.np = None


    def test_basicValidation(self):

        self.assertFalse(self.np.basicValidation(['foo', 'Bar', '2nd']))
        self.assertFalse(self.np.basicValidation(['Foo', 'Bar', 'a123']))
        self.assertFalse(self.np.basicValidation(['Foo', 'Bar', '$123']))
        self.assertFalse(self.np.basicValidation(['Foo', 'Bar', '123']))

        self.assertTrue(self.np.basicValidation(['Foo', 'Bar', '2nd']))


    def test_isPrefix(self):

        self.assertFalse(self.np.isPrefix('foo'))

        self.assertTrue(self.np.isPrefix('Mr'))


    def test_isSuffix(self):

        self.assertFalse(self.np.isSuffix('foo'))

        self.assertTrue(self.np.isSuffix('Sr'))
        self.assertTrue(self.np.isSuffix('IV'))


    def test_isInitial(self):

        self.assertFalse(self.np.isInitial('Hello'))
        self.assertFalse(self.np.isInitial('1'))
        self.assertFalse(self.np.isInitial('1.'))
        self.assertFalse(self.np.isInitial('1,'))
        self.assertFalse(self.np.isInitial('A,'))

        self.assertTrue(self.np.isInitial('Q'))
        self.assertTrue(self.np.isInitial('Q.'))
