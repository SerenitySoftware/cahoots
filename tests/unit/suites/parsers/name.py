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

    def test_basic_validation(self):

        self.assertFalse(self.np.basic_validation(['foo', 'Bar', '2nd']))
        self.assertFalse(self.np.basic_validation(['Foo', 'Bar', 'a123']))
        self.assertFalse(self.np.basic_validation(['Foo', 'Bar', '$123']))
        self.assertFalse(self.np.basic_validation(['Foo', 'Bar', '123']))

        self.assertTrue(self.np.basic_validation(['Foo', 'Bar', '2nd']))

    def test_is_prefix(self):

        self.assertFalse(self.np.is_prefix('foo'))

        self.assertTrue(self.np.is_prefix('Mr'))

    def test_is_suffix(self):

        self.assertFalse(self.np.is_suffix('foo'))

        self.assertTrue(self.np.is_suffix('Sr'))
        self.assertTrue(self.np.is_suffix('IV'))

    def test_is_initial(self):

        self.assertFalse(self.np.is_initial('Hello'))
        self.assertFalse(self.np.is_initial('1'))
        self.assertFalse(self.np.is_initial('1.'))
        self.assertFalse(self.np.is_initial('1,'))
        self.assertFalse(self.np.is_initial('A,'))

        self.assertTrue(self.np.is_initial('Q'))
        self.assertTrue(self.np.is_initial('Q.'))

    def test_parseWithNoUpperCaseLettersYieldsNothing(self):
        count = 0
        for result in self.np.parse('foo'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseWithGreaterThanTenWordsYieldsNothing(self):
        count = 0
        for result in self.np.parse(
                'Foo bar baz buns barf blarg bleh bler blue sner sneh snaf.'
        ):
            count += 1
        self.assertEqual(count, 0)

    def test_parseWithNonBasicValidatedAttributesYieldsNothing(self):
        count = 0
        for result in self.np.parse('Foo bar The Third'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseYieldsExpectedConfidenceWithFiveWordName(self):
        count = 0
        for result in self.np.parse('Dr. Foo Q. Ben Bleh Bar Sr.'):
            self.assertEqual(result.confidence, 65)
            self.assertEqual(result.subtype, 'Name')
            count += 1
        self.assertEqual(count, 1)

    def test_parseYieldsExpectedConfidenceWithThreeWordName(self):
        count = 0
        for result in self.np.parse('Dr. Foo Q. Ben Sr.'):
            self.assertEqual(result.confidence, 95)
            self.assertEqual(result.subtype, 'Name')
            count += 1
        self.assertEqual(count, 1)

    def test_parseYieldsNothingWithOneWordName(self):
        count = 0
        for result in self.np.parse('Foo'):
            count += 1
        self.assertEqual(count, 0)
