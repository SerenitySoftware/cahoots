from brain.util import BrainRegistry, truncateText
import unittest

class BrainRegistryTests(unittest.TestCase):
    """Unit testing of the BrainRegistry"""

    def setUp(self):
        BrainRegistry.storage = {}

    def tearDown(self):
        BrainRegistry.storage = {}

    def test_set(self):

        BrainRegistry.set('test', 'foo')

        self.assertEqual('foo', BrainRegistry.storage['test'])

    def test_test(self):

        BrainRegistry.set('test', 'foo')

        self.assertTrue(BrainRegistry.test('test'))
        self.assertFalse(BrainRegistry.test('bar'))

    def test_get(self):

        BrainRegistry.set('test', 'foo')

        self.assertEqual('foo', BrainRegistry.get('test'))
        self.assertIsNone(BrainRegistry.get('bar'))

    def test_flush(self):

        BrainRegistry.set('test', 'foo')

        self.assertEqual('foo', BrainRegistry.get('test'))
        self.assertNotEqual(0, len(BrainRegistry.storage))

        BrainRegistry.flush()

        self.assertEqual(0, len(BrainRegistry.storage))


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
