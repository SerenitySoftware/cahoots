from brain.parsers.boolean import BooleanParser
import unittest

class BooleanParserTests(unittest.TestCase):
    """Unit Testing of the BooleanParser"""

    bp = None

    trueValues = ["true", "yes", "yep", "yup", "1", "t", "one"]
    falseValues = ["false", "no", "nope", "0", "f", "zero"]
    junkValues = ["asdfasdf", "burp", "2"]


    def setUp(self):
        self.bp = BooleanParser()

    def tearDown(self):
        self.bp = None


    def test_isTrue(self):

        for testValue in self.trueValues:
            self.assertTrue(self.bp.isTrue(testValue))

        for testValue in self.junkValues:
            self.assertFalse(self.bp.isTrue(testValue))

        for testValue in self.falseValues:
            self.assertFalse(self.bp.isTrue(testValue))


    def test_isFalse(self):

        for testValue in self.trueValues:
            self.assertFalse(self.bp.isFalse(testValue))

        for testValue in self.junkValues:
            self.assertFalse(self.bp.isFalse(testValue))

        for testValue in self.falseValues:
            self.assertTrue(self.bp.isFalse(testValue))

