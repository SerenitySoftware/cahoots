from base import BaseParser
from equation import EquationParser
from binascii import unhexlify
from phonenumbers import phonenumberutil
from pyparsing import *
from operator import mul
from SereneRegistry import registry
import re

class NumberParser(BaseParser):

    def __init__(self, config):
        BaseParser.__init__(self, config, "Number", 100)

        def convertToLiteral(s, val):
            return CaselessLiteral(s).setName(s).setParseAction(replaceWith(val))

        self.definedUnits = [
            ("zero",       0),
            ("oh",         0),
            ("zip",        0),
            ("zilch",      0),
            ("nada",       0),
            ("bupkis",     0),
            ("one",        1),
            ("two",        2),
            ("three",      3),
            ("four",       4),
            ("five",       5),
            ("six",        6),
            ("seven",      7),
            ("eight",      8),
            ("nine",       9),
            ("ten",       10),
            ("eleven",    11),
            ("twelve",    12),
            ("thirteen",  13),
            ("fourteen",  14),
            ("fifteen",   15),
            ("sixteen",   16),
            ("seventeen", 17),
            ("eighteen",  18),
            ("nineteen",  19),
        ]

        self.definedTens = [
            ("ten",     10),
            ("twenty",  20),
            ("thirty",  30),
            ("forty",   40),
            ("fourty",  40),
            ("fifty",   50),
            ("sixty",   60),
            ("seventy", 70),
            ("eighty",  80),
            ("ninety",  90),
        ]

        self.definedMajors = [
            ("thousand",          int(1e3)),
            ("million",           int(1e6)),
            ("billion",           int(1e9)),
            ("trillion",          int(1e12)),
            ("quadrillion",       int(1e15)),
            ("quintillion",       int(1e18)),
            ("sextillion",        int(1e21)),
            ("septillion",        int(1e24)),
            ("octillion",         int(1e27)),
            ("nonillion",         int(1e30)),
            ("decillion",         int(1e33)),
            ("undecillion",       int(1e36)),
            ("duodecillion",      int(1e39)),
            ("tredicillion",      int(1e42)),
            ("quattordecillion",  int(1e45)),
            ("quattuordecillion", int(1e45)),
            ("quindecillion",     int(1e48)),
            ("sexdecillion",      int(1e51)),
            ("septendecillion",   int(1e54)),
            ("octodecillion",     int(1e57)),
            ("novemdecillion",    int(1e60)),
            ("vigintillion",      int(1e63)),
        ]

        self.units = Or([convertToLiteral(s, v) for s, v in self.definedUnits])
        self.tens = Or([convertToLiteral(s, v) for s, v in self.definedTens])
        self.hundreds = convertToLiteral("hundred", 100)
        self.majors = Or([convertToLiteral(s, v) for s, v in self.definedMajors])

        self.wordProduct = lambda t: reduce(mul, t)
        self.wordSum = lambda t: sum(t)

        self.numberPartial = (
            (
                (
                    (self.units + Optional(self.hundreds)).setParseAction(self.wordProduct) + 
                    Optional(self.tens)
                ).setParseAction(self.wordSum) 
                ^ self.tens
            ) + Optional(self.units) ).setParseAction(self.wordSum)

        self.numberWords = OneOrMore((self.numberPartial + Optional(self.majors)).setParseAction(self.wordProduct)).setParseAction(self.wordSum) + StringEnd()
        self.numberWords.ignore(CaselessLiteral("-"))
        self.numberWords.ignore(CaselessLiteral("and"))


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
    

    def isFloat(self, data):
        """Checks to see if the value is a float"""
        try:
            return True, float(data)
        except ValueError:
            return False, 0


    def isInteger(self, data):
        """Checks to see if the value is an integer"""
        try:
            return True, int(data)
        except ValueError:
            return False, 0


    def isHex(self, data):
        """Checks to see if the value is hexidecimal"""
        if data[0] == '#':
            data = data[1:]
            
        try:
            return True, int(data, 16)
        except ValueError:
            return False, 0


    def isBinary(self, data):
        """Checks to see if the value looks like a binary"""
        if len(data) < 4:
            return False, 0
        
        if len(data) % 4 != 0:
            return False, 0
            
        for c in data:
            if c not in ["0","1"]:
                return False, 0

        try:
            value = unicode(unhexlify('%x' % int(data, 2)))
        except:
            return False, 0

        return True, value


    def isOctal(self, data):
        """Checks to see if the value is octal"""
        try:
            return True, int(data, 8)
        except ValueError:
            return False, 0


    def isRomanNumeral(self, data):
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
                found = False
                for(roman_numeral, arabic_numeral) in self.roman_numerals:
                    if data[index:(index+len(roman_numeral))] == roman_numeral:
                        value += arabic_numeral
                        index += len(roman_numeral)
                        found = True
                        continue

                if not found:
                    index += 1

            return True, value
            
        return False, 0


    def isWords(self, data):
        try:
            numberValue = self.numberWords.parseString(data)[0]
            return True, numberValue
        except ParseException, pe:
            return False, 0

    def isFraction(self, data):
        """Detects if input is a fraction"""
        if not '/' in data:
            return False, 0

        fraction_split = data.split("/")
        
        if len(fraction_split) > 2:
            return False, 0
        

        whitespace_split = data.split()
        if len(whitespace_split) > 1:
            for whitespace_section in whitespace_split:
                if not self.__recursiveIsNumberCheck(whitespace_section.strip()):
                    return False, 0

        else:
            for split_section in fraction_split:
                if not self.__recursiveIsNumberCheck(split_section):
                    return False, 0
                
        return True, data


    def __recursiveIsNumberCheck(self, data):
        """Calls this parser on a piece of data derived from one of the internal tests"""

        result = self.parse(data)

        try:
            result.next()
            return True
        except StopIteration:
            return False

        return False


    def parse(self, data, **kwargs):
        data = data.strip()

        if data == "":
            return
            
        if data[0] == "-":
            data = data[1:]

        data = data.replace(",", "")
        
        if data == '':
            return
        
        is_fraction, value = self.isFraction(data)
        if is_fraction:
            fraction_confidence = 100

            # for every character in the data other than the /, we lower the confidence a bit. Fractions are USUALLY short
            for c in data:
                if c != "/":
                    fraction_confidence -= 3

            # if the fraction isn't solve-able, we lower the confidence significantly
            # it might "technically" be a fraction made up of roman numerals, etc.
            if EquationParser in self.Config.enabledModules:
                ep = EquationParser(self.Config)
                if not ep.solveEquation(ep.autoFloat(data)):
                    fraction_confidence -= 40

            yield self.result("Fraction", fraction_confidence, value)
            return
                    

        is_binary, value = self.isBinary(data)
        if is_binary:
            yield self.result("Binary", 100, value)
            return


        is_integer, value = self.isInteger(data)
        if is_integer:
            integer_confidence = 75
            octal_confidence = 25

            try:
                phonenumberutil.parse(data, _check_region=False)
                # 10 point confidence penalty
                integer_confidence -= 10
            except:
                pass

            is_octal, octal_value = self.isOctal(data)
            if is_octal:
                yield self.result("Integer", integer_confidence, value)
                yield self.result("Octal", octal_confidence, octal_value)
                return

            # Just an int
            yield self.result("Integer", integer_confidence, value)
            return
            

        if '.' in data:
            is_float, value = self.isFloat(data)
            if is_float:
                yield self.result("Decimal", 100, value)
                return
            

        if len(data) > 1:
            is_hex, value = self.isHex(data)
            if is_hex:
                yield self.result("Hexadecimal", 100, value)
                return
            
        is_roman_numeral, value = self.isRomanNumeral(data)
        if is_roman_numeral:
            yield self.result("Roman Numeral", 100, value)
            return

        is_word, value = self.isWords(data)
        if is_word:
            yield self.result("Word Number", 100, value)
            return