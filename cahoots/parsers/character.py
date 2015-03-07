from base import BaseParser
from boolean import BooleanParser
import string


class CharacterParser(BaseParser):

    def __init__(self, config):
        BaseParser.__init__(self, config, "Character", 25)

    def isLetter(self, data):
        """Checks if input is a letter"""
        if data in string.ascii_letters:
            return True

        return False

    def isPunctuation(self, data):
        """Checks if input is punctuation"""
        if data in string.punctuation:
            return True

        return False

    def isWhitespace(self, data):
        """Checks if input is whitespace"""
        if data in string.whitespace:
            return True

        return False

    def parse(self, data, **kwargs):
        if len(data) != 1:
            return

        characterData = {
            'char-code': ord(data)
        }

        # If this character doesn't evaluate as a boolean, we're positive
        # it's a character if it passes one of the specific evaulations.
        if BooleanParser in self.Config.enabledModules:
            bp = BooleanParser(self.Config)
            if not bp.isTrue(data) and not bp.isFalse(data):
                self.confidence = 100

        if self.isLetter(data):
            yield self.result("Letter", data=characterData)

        elif self.isPunctuation(data):
            yield self.result("Punctuation", data=characterData)

        elif self.isWhitespace(data):
            yield self.result("Whitespace", data=characterData)
