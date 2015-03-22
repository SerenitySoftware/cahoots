"""
The MIT License (MIT)

Copyright (c) Serenity Software, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from cahoots.parsers.base import BaseParser
from cahoots.parsers.boolean import BooleanParser
import string


class CharacterParser(BaseParser):
    '''Determines if given data is a character'''

    def __init__(self, config):
        BaseParser.__init__(self, config, "Character", 25)

    @classmethod
    def is_letter(cls, data):
        """Checks if input is a letter"""
        if data in string.ascii_letters:
            return True

        return False

    @classmethod
    def is_punctuation(cls, data):
        """Checks if input is punctuation"""
        if data in string.punctuation:
            return True

        return False

    @classmethod
    def is_whitespace(cls, data):
        """Checks if input is whitespace"""
        if data in string.whitespace:
            return True

        return False

    def parse(self, data):
        if len(data) != 1:
            return

        character_data = {
            'char-code': ord(data)
        }

        # If this character doesn't evaluate as a boolean, we're positive
        # it's a character if it passes one of the specific evaulations.
        data = data.lower()
        if not BooleanParser.is_true(data) and \
                not BooleanParser.is_false(data):
            self.confidence = 100

        if self.is_letter(data):
            yield self.result("Letter", data=character_data)

        elif self.is_punctuation(data):
            yield self.result("Punctuation", data=character_data)

        elif self.is_whitespace(data):
            yield self.result("Whitespace", data=character_data)
