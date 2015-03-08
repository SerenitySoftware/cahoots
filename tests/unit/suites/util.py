from cahoots.util import truncate_text, is_number
import unittest


class TruncateTextTests(unittest.TestCase):

    testString = 'The quick brown fox jumps over the lazy dog'

    def test_too_short_string(self):
        self.assertEquals(truncate_text(self.testString), self.testString)

    def test_short_limit(self):
        self.assertEquals(truncate_text(self.testString, 10), 'The qui...')

    def test_too_long_string(self):
        testString = 'Lorem ipsum dolor sit amet, consectetur adipiscing' \
                     ' elit. Suspendisse non risus risus amet.'
        truncatedTestString = 'Lorem ipsum dolor sit amet, consectetur' \
                              ' adipiscing elit. Suspendisse non risu...'

        self.assertEquals(truncate_text(testString), truncatedTestString)


class IsNumberTests(unittest.TestCase):

    def test_is_number(self):

        self.assertTrue(is_number("123.123"))
        self.assertTrue(is_number("123"))

        self.assertFalse(is_number("7 divided by 2"))
