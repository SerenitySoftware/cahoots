from brain.result import ParseResult, ParseResultMulti
from base import BaseParser
from equation import EquationParser
from binascii import unhexlify
from phonenumbers import phonenumberutil
import re

class NumberParser(BaseParser):

    def __init__(self):
        self.Type = "Number"
        self.Confidence = 100


    def isFloat(self, data):
        """Checks to see if the value is a float"""
        try:
            float(data)
            return True
        except ValueError:
            return False


    def isInteger(self, data):
        """Checks to see if the value is an integer"""
        try:
            int(data)
            return True
        except ValueError:
            return False


    def isHex(self, data):
        """Checks to see if the value is hexidecimal"""
        if data[0] == '#':
            data = data[1:]
            
        try:
            int(data, 16)
            return True
        except ValueError:
            return False


    def isBinary(self, data):
        """Checks to see if the value looks like a binary"""
        if len(data) < 4:
            return False
        
        if len(data) % 4 != 0:
            return False
            
        for c in data:
            if c not in ["0","1"]:
                return False
                
        return True


    def decodeBinary(self, data):
        """Tries to take something that we've decided looks like a binary, and decode it"""
        try:
            return unicode(unhexlify('%x' % int(data, 2)))
        except:
            return False


    def isOctal(self, data):
        """Checks to see if the value is octal"""
        try:
            int(data, 8)
            return True
        except ValueError:
            return False


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
            return True
            
        return False


    def isFraction(self, data):
        """Detects if input is a fraction"""
        if not '/' in data:
            return False

        fraction_split = data.split("/")
        
        if len(fraction_split) > 2:
            return False
        

        whitespace_split = data.split()
        if len(whitespace_split) > 1:
            for whitespace_section in whitespace_split:
                if not self.__recursiveIsNumberCheck(whitespace_section.strip()):
                    return False

        else:
            for split_section in fraction_split:
                if not self.__recursiveIsNumberCheck(split_section):
                    return False
                
        return True


    def __recursiveIsNumberCheck(self, data):
        """Calls this parser on a piece of data derived from one of the internal tests"""

        result = self.parse(data)

        if isinstance(result, ParseResultMulti) or result.Matched:
            return True

        return False


    def parse(self, data, **kwargs):
        data = data.strip()

        if data == "":
            return self.result(False)
            
        if data[0] == "-":
            data = data[1:]

        data = data.replace(",", "")
        
        if data == '':
            return self.result(False)
        

        if self.isFraction(data):

            # for every character in the data other than the /, we lower the confidence a bit. Fractions are USUALLY short
            for c in data:
                if c != "/":
                    self.Confidence -= 3

            # if the fraction isn't solve-able, we lower the confidence significantly
            # it might "technically" be a fraction made up of roman numerals, etc.
            ep = EquationParser()
            if not ep.solveEquation(ep.autoFloat(data)):
                self.Confidence -= 40

            return self.result(True, "Fraction")
                    

        if self.isBinary(data):

            decodedBinary = self.decodeBinary(data)
            if not decodedBinary:
                self.Confidence -= 75
                return self.result(True, "Binary")
            else:
                return self.result(True, "Binary", data=decodedBinary)
         

        if self.isInteger(data):


            try:
                phonenumberutil.parse(data, _check_region=False)
                # 10 point confidence penalty
                cp = 10
            except:
                cp = 0
                pass

            if self.isOctal(data):
                return self.resultMulti({'Integer': 75-(cp/2),'Octal': 25-(cp/2)})

            # Just an int
            return self.result(True, "Integer", self.Confidence - cp)
            

        if '.' in data and self.isFloat(data):
            return self.result(True, "Decimal")    
            

        if len(data) > 1 and self.isHex(data):
            return self.result(True, "Hexadecimal")
            

        if self.isRomanNumeral(data):
            return self.result(True, "Roman Numeral")
            

        return self.result(False)
    


    def resultMulti(self, resultData):
        """Prepares a ParseResultMulti object containing the numbers detected"""

        return ParseResultMulti([ParseResult(True, self.Type, subType, confidence) for subType, confidence in resultData.items()])
