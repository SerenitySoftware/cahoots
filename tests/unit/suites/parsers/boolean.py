from cahoots.parsers.boolean import BooleanParser
from cahoots.result import ParseResult
from tests.unit.config import TestConfig
import unittest


class BooleanParserTests(unittest.TestCase):
    """Unit Testing of the BooleanParser"""

    bp = None

    trueValues = ["true", "yes", "yep", "yup", "1", "t", "one"]
    falseValues = ["false", "no", "nope", "0", "f", "zero"]
    junkValues = ["asdfasdf", "burp", "2"]

    def setUp(self):
        self.bp = BooleanParser(TestConfig())

    def tearDown(self):
        self.bp = None

    def test_is_true(self):

        for testValue in self.trueValues:
            self.assertTrue(self.bp.is_true(testValue))

        for testValue in self.junkValues:
            self.assertFalse(self.bp.is_true(testValue))

        for testValue in self.falseValues:
            self.assertFalse(self.bp.is_true(testValue))

    def test_is_false(self):

        for testValue in self.trueValues:
            self.assertFalse(self.bp.is_false(testValue))

        for testValue in self.junkValues:
            self.assertFalse(self.bp.is_false(testValue))

        for testValue in self.falseValues:
            self.assertTrue(self.bp.is_false(testValue))

    def test_parseLongStringYieldsNothing(self):
        resultTest = None

        for result in self.bp.parse("LookALongString"):
            resultTest = result

        self.assertIsNone(resultTest)

    def test_parseTrueValuesYieldsExpectedConfidence(self):
        valueConfidence = [("true", 100),
                           ("yes", 100),
                           ("yep", 75),
                           ("yup", 75),
                           ("1", 50),
                           ("t", 50),
                           ("one", 50)]

        for value, confidence in valueConfidence:
            for result in self.bp.parse(value):
                self.assertIsInstance(result, ParseResult)
                self.assertEqual(result.confidence, confidence)
                self.assertTrue(result.result_value)

    def test_parseFalseValuesYieldsExpectedConfidence(self):
        valueConfidence = [("false", 100),
                           ("no", 100),
                           ("nope", 75),
                           ("0", 50),
                           ("f", 50),
                           ("zero", 50)]

        for value, confidence in valueConfidence:
            for result in self.bp.parse(value):
                self.assertIsInstance(result, ParseResult)
                self.assertEqual(result.confidence, confidence)
                self.assertFalse(result.result_value)

    def test_parseTrueValuesYieldsNothing(self):
        resultTest = None

        for value in self.junkValues:
            for result in self.bp.parse(value):
                resultTest = result

        self.assertIsNone(resultTest)
