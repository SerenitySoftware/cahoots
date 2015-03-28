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
from cahoots.parsers.number import NumberParser
import re
import string


class NameParser(BaseParser):
    '''Determines if given data is a name'''

    prefixes = ['MS', 'MISS', 'MRS', 'MR', 'MASTER', 'REV', 'FR', 'DR',
                'ATTY', 'PROF', 'HON', 'PRES', 'GOV', 'COACH', 'OFC', 'MSGR',
                'SR', 'BR', 'SUPT', 'REP', 'SEN', 'AMB', 'TREAS', 'SEC',
                'PVT', 'CPL', 'SGT', 'ADM', 'MAJ', 'CAPT', 'CMDR', 'LT',
                'COL', 'GEN']
    suffixes = ['AB', 'BA', 'BFA', 'BTECH', 'LLB', 'BSC', 'MA', 'MFA', 'LLM',
                'MLA', 'MBA', 'MSC', 'JD', 'MD', 'DO', 'PHARMD', 'PHD',
                'DPHIL', 'LLD', 'ENGD', 'KBE', 'LLD', 'DD', 'ESQ', 'ESQUIRE',
                'CSA', 'ASCAP', 'CA', 'CPA', 'CFA', 'PE', 'PG', 'CPL', 'CENG',
                'RA', 'AIA', 'RIBA', 'MEOA', 'CISA', 'CISSP', 'CISM', 'PT',
                'DPT', 'MCSP', 'SRP', 'RGN', 'USN', 'USMC', 'OFM', 'CSV',
                'JR', 'SR', 'JNR', 'SNR', '2ND', '3RD', '4TH', '5TH', '6TH',
                '7TH', '8TH', '9TH', 'BT', 'BART', 'QC', 'MP', 'SSF', 'FRCP',
                'FRSA', 'RAF', 'RN', 'RMP', 'FAIA', 'FRSE', 'SJ', 'OP',
                'ICMA-CM', 'MBASW']

    def __init__(self, config):
        BaseParser.__init__(self, config, "Name", 0)

    @classmethod
    def basic_validation(cls, data):
        """
        Make sure every word in the phrase either
        starts with a Capital Letter or a Number
        """
        return len(data) == len(
            [word for word in data if
             # Has to start with a capital letter or digit
             (word[0].isupper() or (len(data) > 1 and word[0].isdigit())) and
             # Whole word can't be a digit
             not word.isdigit() and
             # Must contain only printable characters
             not [char for char in word if char not in string.printable]]
        )

    def is_prefix(self, word):
        """Checks to see if the word passed in is a name prefix"""
        word = word.replace('.', '').upper()
        return word in self.prefixes

    def is_suffix(self, word):
        """Checks to see if the word passed in is a name suffix"""
        if NumberParser in self.config.enabled_modules:
            nump = NumberParser(self.config)
            if nump.is_roman_numeral(word) != (False, 0):
                return True

        word = word.replace('.', '').upper()
        return word in self.suffixes

    @classmethod
    def is_initial(cls, word):
        """Checks to see if the word passed in is an initial"""
        if len(word) > 2:
            return False

        if len(word) == 1:
            return word[0].isalpha()

        if len(word) == 2:
            return word[1] == '.' and word[0].isalpha()

    def detect_prefix_or_suffix(self, data):
        """
        Checking for things like Mr. or Jr. Big boost for these values.
        If found, we remove them from the list of words
        """
        if len(data) > 2:
            if self.is_prefix(data[0]):
                data.pop(0)
                self.confidence += 20
            if self.is_suffix(data[-1]):
                data.pop()
                self.confidence += 20

    def calculate_confidence(self, data):
        '''Calculates confidence based on various attributes of the data'''

        # If we have a two - four word "name" here we boost its
        # confidence since this is something of a giveaway
        if len(data) in xrange(2, 4):
            self.confidence += (5 * len(data))

        # Adding confidence for initials vs words,
        # if we have greater than one word
        if len(data) > 1:
            for word in data:
                if self.is_initial(word):
                    self.confidence += 15
                    # if there's a period in this initial, we boost it.
                    if "." in word:
                        self.confidence += 5
                else:
                    self.confidence += 10

        # If our "name" is longer than 4 words, we
        # reduce the likelihood that it's a name
        if len(data) > 3:
            self.confidence -= (7*len(data))

    def parse(self, data):
        """Determines if the data is a name or not"""

        # Making sure there are at least SOME uppercase letters in the phrase
        if not re.search('[A-Z]', data):
            return

        data = data.split()

        # If someone has a name longer than 7 words...they need
        # help. Making sure each word in the phrase starts with an
        # uppercase letter or a number
        if len(data) >= 7 or not self.basic_validation(data):
            return

        self.detect_prefix_or_suffix(data)

        self.calculate_confidence(data)

        if self.confidence <= 0:
            return

        yield self.result("Name", min(100, self.confidence))
