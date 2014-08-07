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

    def test_isLetter(self):
        self.assertTrue(self.cp.isLetter("a"))
        self.assertFalse(self.cp.isLetter("1"))
        self.assertFalse(self.cp.isLetter("."))
        self.assertFalse(self.cp.isLetter(" "))
        self.assertFalse(self.cp.isLetter("asdf"))

    def test_isPunctuation(self):
        self.assertTrue(self.cp.isPunctuation("."))
        self.assertFalse(self.cp.isPunctuation("1"))
        self.assertFalse(self.cp.isPunctuation("a"))
        self.assertFalse(self.cp.isPunctuation(" "))
        self.assertFalse(self.cp.isPunctuation("asdf"))

    def test_isWhitespace(self):
        self.assertTrue(self.cp.isWhitespace(" "))
        self.assertFalse(self.cp.isWhitespace("1"))
        self.assertFalse(self.cp.isWhitespace("a"))
        self.assertFalse(self.cp.isWhitespace("."))
        self.assertFalse(self.cp.isWhitespace("asdf"))

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
            self.assertEqual(result.Subtype, 'Letter')
            self.assertEqual(result.Data, {'char-code': 97})
            self.assertEqual(result.Confidence, 100)
        self.assertEqual(count, 1)

    def test_parsePunctuationYieldsProperResult(self):
        count = 0
        for result in self.cp.parse('.'):
            count += 1
            self.assertEqual(result.Subtype, 'Punctuation')
            self.assertEqual(result.Data, {'char-code': 46})
            self.assertEqual(result.Confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWhitespaceYieldsProperResult(self):
        count = 0
        for result in self.cp.parse(' '):
            count += 1
            self.assertEqual(result.Subtype, 'Whitespace')
            self.assertEqual(result.Data, {'char-code': 32})
            self.assertEqual(result.Confidence, 100)
        self.assertEqual(count, 1)

    def test_parseBooleanLetterYieldsLowerConfidence(self):
        count = 0
        for result in self.cp.parse('t'):
            count += 1
            self.assertEqual(result.Subtype, 'Letter')
            self.assertEqual(result.Data, {'char-code': 116})
            self.assertEqual(result.Confidence, 25)
        self.assertEqual(count, 1)
