from cahoots.util import CahootsRegistry, truncateText, isNumber
import unittest

class CahootsRegistryTests(unittest.TestCase):
    """Unit testing of the CahootsRegistry"""

    def setUp(self):
        CahootsRegistry.storage = {}

    def tearDown(self):
        CahootsRegistry.storage = {}

    def test_set(self):

        CahootsRegistry.set('test', 'foo')

        self.assertEqual('foo', CahootsRegistry.storage['test'])

    def test_test(self):

        CahootsRegistry.set('test', 'foo')

        self.assertTrue(CahootsRegistry.test('test'))
        self.assertFalse(CahootsRegistry.test('bar'))

    def test_get(self):

        CahootsRegistry.set('test', 'foo')

        self.assertEqual('foo', CahootsRegistry.get('test'))
        self.assertIsNone(CahootsRegistry.get('bar'))

    def test_flush(self):

        CahootsRegistry.set('test', 'foo')

        self.assertEqual('foo', CahootsRegistry.get('test'))
        self.assertNotEqual(0, len(CahootsRegistry.storage))

        CahootsRegistry.flush()

        self.assertEqual(0, len(CahootsRegistry.storage))


class truncateTextTests(unittest.TestCase):

    testString = 'The quick brown fox jumps over the lazy dog'
    
    def test_too_short_string(self):
        self.assertEquals(truncateText(self.testString), self.testString)

    def test_short_limit(self):
        self.assertEquals(truncateText(self.testString, 10), 'The qui...')

    def test_too_long_string(self):
        testString = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse non risus risus amet.'
        truncatedTestString = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse non risu...'

        self.assertEquals(truncateText(testString), truncatedTestString)


class isNumberTests(unittest.TestCase):

    def test_isNumber(self):

        self.assertTrue(isNumber("123.123"))
        self.assertTrue(isNumber("123"))

        self.assertFalse(isNumber("7 divided by 2"))