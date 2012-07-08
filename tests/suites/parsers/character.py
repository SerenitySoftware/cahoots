from brain.parsers.character import CharacterParser
import unittest

class CharacterParserTests(unittest.TestCase):
    """Unit Testing of the CharacterParser"""

    cp = None

    def setUp(self):
        self.cp = CharacterParser()

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