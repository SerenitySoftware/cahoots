from cahoots.parsers.character import CharacterParser
from tests.unit.config import TestConfig
import unittest


class CharacterParserTests(unittest.TestCase):
    """Unit Testing of the CharacterParser"""

    cp = None

    def setUp(self):
        self.cp = CharacterParser(TestConfig())

    def tearDown(self):
        self.cp = None

    def test_is_letter(self):
        self.assertTrue(self.cp.is_letter("a"))
        self.assertFalse(self.cp.is_letter("1"))
        self.assertFalse(self.cp.is_letter("."))
        self.assertFalse(self.cp.is_letter(" "))
        self.assertFalse(self.cp.is_letter("asdf"))

    def test_is_punctuation(self):
        self.assertTrue(self.cp.is_punctuation("."))
        self.assertFalse(self.cp.is_punctuation("1"))
        self.assertFalse(self.cp.is_punctuation("a"))
        self.assertFalse(self.cp.is_punctuation(" "))
        self.assertFalse(self.cp.is_punctuation("asdf"))

    def test_is_whitespace(self):
        self.assertTrue(self.cp.is_whitespace(" "))
        self.assertFalse(self.cp.is_whitespace("1"))
        self.assertFalse(self.cp.is_whitespace("a"))
        self.assertFalse(self.cp.is_whitespace("."))
        self.assertFalse(self.cp.is_whitespace("asdf"))

    def test_parseReturnsNothingWithStringLongerThanOneCharacter(self):
        count = 0
        for result in self.cp.parse("asdf"):
            count += 1
        self.assertEqual(count, 0)

    def test_parseNonAsciiCharacterReturnNone(self):
        count = 0
        for result in self.cp.parse(u'\u0080'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseLetterYieldsProperResult(self):
        count = 0
        for result in self.cp.parse('a'):
            count += 1
            self.assertEqual(result.subtype, 'Letter')
            self.assertEqual(result.data, {'char-code': 97})
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parsePunctuationYieldsProperResult(self):
        count = 0
        for result in self.cp.parse('.'):
            count += 1
            self.assertEqual(result.subtype, 'Punctuation')
            self.assertEqual(result.data, {'char-code': 46})
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWhitespaceYieldsProperResult(self):
        count = 0
        for result in self.cp.parse(' '):
            count += 1
            self.assertEqual(result.subtype, 'Whitespace')
            self.assertEqual(result.data, {'char-code': 32})
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseBooleanLetterYieldsLowerConfidence(self):
        count = 0
        for result in self.cp.parse('t'):
            count += 1
            self.assertEqual(result.subtype, 'Letter')
            self.assertEqual(result.data, {'char-code': 116})
            self.assertEqual(result.confidence, 25)
        self.assertEqual(count, 1)
