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
import string


class CharacterParser(BaseParser):
    '''Determines if given data is a character'''

    def __init__(self, config):
        """
        :param config: cahoots config
        :type config: cahoots.config.BaseConfig
        """
        BaseParser.__init__(self, config, "Character", 25)

    @classmethod
    def is_letter(cls, data):
        """
        Checks if input is a letter

        :param data: data that might be a letter
        :type data: str
        :return: if it's a letter or not
        :rtype: bool
        """
        if data in string.ascii_letters:
            return True

        return False

    @classmethod
    def is_punctuation(cls, data):
        """
        Checks if input is punctuation

        :param data: data that might be punctuation
        :type data: str
        :return: if it's punctuation or not
        :rtype: bool
        """
        if data in string.punctuation:
            return True

        return False

    @classmethod
    def is_whitespace(cls, data):
        """
        Checks if input is whitespace

        :param data: data that might be whitespace
        :type data: str
        :return: if it's whitespace or not
        :rtype: bool
        """
        if data in string.whitespace:
            return True

        return False

    def parse(self, data):
        """
        parses for characters

        :param data: the string we want to parse
        :type data: str
        :return: yields parse result(s) if there are any
        :rtype: ParseResult
        """
        if len(data) != 1:
            return

        character_data = {
            'char-code': ord(data)
        }

        if self.is_letter(data):
            yield self.result("Letter", data=character_data)

        elif self.is_punctuation(data):
            yield self.result("Punctuation", data=character_data)

        elif self.is_whitespace(data):
            yield self.result("Whitespace", data=character_data)
