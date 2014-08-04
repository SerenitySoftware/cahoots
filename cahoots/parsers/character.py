from base import BaseParser
from boolean import BooleanParser
import string
from SereneRegistry import registry

class CharacterParser(BaseParser):

    def __init__(self):
        self.Type = "Character"
        self.Confidence = 25
    
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

        try:
            data = data.decode('utf-8')
        except:
            return
        
        try:
            ascii_version = ord(data)
        except UnicodeEncodeError:
            ascii_version = None
            
        try:
            utf8_version = ord(unicode(data))
        except UnicodeEncodeError:
            utf8_version = None
            
        characterData = {
            "ascii": ascii_version,
            "utf-8": utf8_version
        }

        # If this character doesn't evaluate as a boolean, we're positive
        # it's a character if it passes one of the specific evaulations.
        if BooleanParser in registry.get('Config').enabledModules:
            bp = BooleanParser()
            if not bp.isTrue(data) and not bp.isFalse(data):
                self.Confidence = 100
            
        if self.isLetter(data):
            yield self.result("Letter", data = characterData)
            
        if self.isPunctuation(data):
            yield self.result("Punctuation", data = characterData)
            
        if self.isWhitespace(data):
            yield self.result("Whitespace", data = characterData)
            