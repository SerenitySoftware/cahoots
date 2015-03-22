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
# pylint: disable=unnecessary-lambda
# pylint: disable=too-many-instance-attributes
from cahoots.parsers.base import BaseParser
from cahoots.parsers.phone import PhoneParser
from cahoots.parsers.equation import EquationParser
from binascii import unhexlify
from pyparsing import\
    Or, \
    OneOrMore, \
    Optional, \
    CaselessLiteral, \
    StringEnd, \
    ParseException, \
    replaceWith
from operator import mul
import re
from cahoots.result import ParseResult


class NumberParser(BaseParser):
    """determines if given data is one of many types of numbers"""

    def __init__(self, config):
        BaseParser.__init__(self, config, "Number", 100)

        def convert_to_literal(tok, val):
            """Converts a value to pyparsing caselessliteral"""
            return CaselessLiteral(tok) \
                .setName(tok) \
                .setParseAction(replaceWith(val))

        self.defined_units = [
            ("zero", 0),
            ("oh", 0),
            ("zip", 0),
            ("zilch", 0),
            ("nada", 0),
            ("bupkis", 0),
            ("one", 1),
            ("two", 2),
            ("three", 3),
            ("four", 4),
            ("five", 5),
            ("six", 6),
            ("seven", 7),
            ("eight", 8),
            ("nine", 9),
            ("ten", 10),
            ("eleven", 11),
            ("twelve", 12),
            ("thirteen", 13),
            ("fourteen", 14),
            ("fifteen", 15),
            ("sixteen", 16),
            ("seventeen", 17),
            ("eighteen", 18),
            ("nineteen", 19),
        ]

        self.defined_tens = [
            ("ten", 10),
            ("twenty", 20),
            ("thirty", 30),
            ("forty", 40),
            ("fourty", 40),
            ("fifty", 50),
            ("sixty", 60),
            ("seventy", 70),
            ("eighty", 80),
            ("ninety", 90),
        ]

        self.defined_majors = [
            ("thousand", int(1e3)),
            ("million", int(1e6)),
            ("billion", int(1e9)),
            ("trillion", int(1e12)),
            ("quadrillion", int(1e15)),
            ("quintillion", int(1e18)),
            ("sextillion", int(1e21)),
            ("septillion", int(1e24)),
            ("octillion", int(1e27)),
            ("nonillion", int(1e30)),
            ("decillion", int(1e33)),
            ("undecillion", int(1e36)),
            ("duodecillion", int(1e39)),
            ("tredicillion", int(1e42)),
            ("quattordecillion", int(1e45)),
            ("quattuordecillion", int(1e45)),
            ("quindecillion", int(1e48)),
            ("sexdecillion", int(1e51)),
            ("septendecillion", int(1e54)),
            ("octodecillion", int(1e57)),
            ("novemdecillion", int(1e60)),
            ("vigintillion", int(1e63)),
        ]

        self.units = Or(
            [convert_to_literal(s, v) for s, v in self.defined_units]
        )
        self.tens = Or(
            [convert_to_literal(s, v) for s, v in self.defined_tens]
        )
        self.hundreds = convert_to_literal("hundred", 100)
        self.majors = Or(
            [convert_to_literal(s, v) for s, v in self.defined_majors]
        )

        self.word_product = lambda t: reduce(mul, t)
        self.word_sum = lambda t: sum(t)

        self.number_partial = (
            (
                (
                    (
                        self.units + Optional(self.hundreds)
                    ).setParseAction(self.word_product) + Optional(self.tens)
                ).setParseAction(self.word_sum) ^ self.tens
            ) + Optional(self.units)).setParseAction(self.word_sum)

        self.number_words = OneOrMore(
            (self.number_partial +
             Optional(self.majors)).setParseAction(self.word_product)
        ).setParseAction(self.word_sum) + StringEnd()

        self.number_words.ignore(CaselessLiteral("-"))
        self.number_words.ignore(CaselessLiteral("and"))

        self.roman_numerals = [
            ['M', 1000],
            ['CM', 900],
            ['D', 500],
            ['CD', 400],
            ['C', 100],
            ['XC', 90],
            ['L', 50],
            ['XL', 40],
            ['X', 10],
            ['IX', 9],
            ['V', 5],
            ['IV', 4],
            ['I', 1]
        ]

    @classmethod
    def is_float(cls, data):
        """Checks to see if the value is a float"""
        try:
            return True, float(data)
        except ValueError:
            return False, 0

    @classmethod
    def is_integer(cls, data):
        """Checks to see if the value is an integer"""
        try:
            return True, int(data)
        except ValueError:
            return False, 0

    @classmethod
    def is_hex(cls, data):
        """Checks to see if the value is hexidecimal"""
        if data[0] == '#':
            data = data[1:]

        try:
            return True, int(data, 16)
        except ValueError:
            return False, 0

    @classmethod
    def is_binary(cls, data):
        """Checks to see if the value looks like a binary"""
        if len(data) < 4:
            return False, 0

        if len(data) % 4 != 0:
            return False, 0

        for char in data:
            if char not in ["0", "1"]:
                return False, 0

        try:
            value = unicode(unhexlify('%x' % int(data, 2)))
        except (ValueError, TypeError):
            return False, 0

        return True, value

    @classmethod
    def is_octal(cls, data):
        """Checks to see if the value is octal"""
        try:
            return True, int(data, 8)
        except ValueError:
            return False, 0

    def is_roman_numeral(self, data):
        """Checks to see if the value is a roman numeral"""
        data = data.upper()
        rgx_roman = re.compile("""^
           ([M]{0,9})   # thousands
           ([DCM]*)     # hundreds
           ([XLC]*)     # tens
           ([IVX]*)     # units
           $""", re.VERBOSE)

        match = rgx_roman.match(data)

        if match:
            value = 0
            index = 0

            while index < len(data):
                for(roman_numeral, arabic_numeral) in self.roman_numerals:
                    if data[index:(index+len(roman_numeral))] == roman_numeral:
                        value += arabic_numeral
                        index += len(roman_numeral)
                        continue

            return True, value

        return False, 0

    def is_words(self, data):
        """determines if the data is textual numbers"""
        try:
            number_value = self.number_words.parseString(data)[0]
            return True, number_value
        except ParseException:
            return False, 0

    def is_fraction(self, data):
        """Detects if input is a fraction"""
        if '/' not in data:
            return False, 0

        fraction_split = data.split("/")

        if len(fraction_split) > 2:
            return False, 0

        whitespace_split = data.split()
        if len(whitespace_split) > 1:
            for whitespace_section in whitespace_split:
                test = whitespace_section.strip()
                if (
                        self.is_fraction(test) == (False, 0) and
                        self.is_integer(test) == (False, 0)
                ):
                    return False, 0

        else:
            for split_section in fraction_split:
                test = split_section.strip()
                if (
                        len(test) == 0 or
                        self.is_integer(split_section.strip()) == (False, 0)
                ):
                    return False, 0

        return True, data

    @classmethod
    def prep_data(cls, data):
        """Removes unwanted stuff from data"""
        data = data.strip()

        if not data:
            return data

        if data[0] == "-":
            data = data[1:]

        return data.replace(",", "")

    def parse_fraction(self, data):
        """finds and confidence scores a fraction"""
        is_fraction, value = self.is_fraction(data)
        if is_fraction:
            fraction_confidence = 100

            # for every character in the data other than the /, we lower
            # the confidence a bit. Fractions are USUALLY short
            for char in data:
                if char != "/":
                    fraction_confidence -= 3

            # if the fraction isn't solve-able, we lower the confidence
            # significantly it might "technically" be a fraction made up
            # of roman numerals, etc.
            if EquationParser in self.config.enabledModules:
                eqp = EquationParser(self.config)
                if not eqp.solve_equation(eqp.auto_float(data)):
                    fraction_confidence -= 40

            return self.result("Fraction", fraction_confidence, value)

    def parse_binary(self, data):
        """finds and confidence scores a binary"""
        is_binary, value = self.is_binary(data)
        if is_binary:
            return self.result("Binary", 100, value)

    def parse_integer(self, data):
        """finds and confidence scores a integer"""
        is_integer, value = self.is_integer(data)
        if is_integer:
            integer_confidence = 75
            octal_confidence = 25

            # 10 point confidence penalty if int is also a phone number
            if PhoneParser in self.config.enabledModules:
                PhoneParser.bootstrap(self.config)
                phone_parser = PhoneParser(self.config)
                for _ in phone_parser.parse(data):
                    integer_confidence -= 10

            is_octal, octal_value = self.is_octal(data)
            if is_octal:
                return [
                    self.result("Integer", integer_confidence, value),
                    self.result("Octal", octal_confidence, octal_value)
                ]

            # Just an int
            return self.result("Integer", integer_confidence, value)

    def parse_float(self, data):
        """finds and confidence scores a float"""
        if '.' in data:
            is_float, value = self.is_float(data)
            if is_float:
                return self.result("Decimal", 100, value)

    def parse_hex(self, data):
        """finds and confidence scores a hex number"""
        if len(data) > 1:
            is_hex, value = self.is_hex(data)
            if is_hex:
                return self.result("Hexadecimal", 100, value)

    def parse_roman_numeral(self, data):
        """finds and confidence scores a roman numeral"""
        is_roman_numeral, value = self.is_roman_numeral(data)
        if is_roman_numeral:
            return self.result("Roman Numeral", 100, value)

    def parse_word_number(self, data):
        """finds and confidence scores a word-number"""
        is_word, value = self.is_words(data)
        if is_word:
            return self.result("Word Number", 100, value)

    def parse(self, data):
        data = self.prep_data(data)

        if not data:
            return

        # cascading through our potential parsers until we find something
        results = \
            self.parse_fraction(data) or \
            self.parse_binary(data) or \
            self.parse_integer(data) or \
            self.parse_float(data) or \
            self.parse_hex(data) or \
            self.parse_roman_numeral(data) or \
            self.parse_word_number(data)

        if results:
            if not isinstance(results, list):
                results = [results]
            for result in results:
                if isinstance(result, ParseResult):
                    yield result
