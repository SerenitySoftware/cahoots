from brain.util import isNumber
from base import BaseParser
from phonenumbers import phonenumberutil
from programming import ProgrammingParser
import re, string, math, config


class EquationParser(BaseParser):
    """
    brain.parsers.equation
    parser to identify and solve some mathematical equations
    """

    __parsedEquation = None
    """After we've processed the input string from the user, this var will contain the assembled result"""


    def __init__(self):
        self.Type = "Equation"
        self.Confidence = 100


    def isSimpleEquation(self, data):
        """Seeing if our string only has symbols found in simple math equations"""

        rgx = re.compile("""^
           ([()*.\-+0-9^/ ])*
           $""", re.VERBOSE)
           
        match = rgx.match(data)
        
        if match:
            data = self.autoFloat(data)
            self.__parsedEquation = self.autoMultiply(data)
            return True
            
        return False
    
    
    def isTextEquation(self, data):
        """Searching for specific textual markers that can be converted into mathematical operators"""
        
        # SQUARE ROOTS
        parsedData = re.compile('SQUARE[ ]{1,}ROOT[ ]{1,}OF[ ]{1,}\d+(\.\d+)?').sub(self.__squareRootTextReplace, data)
        
        # Simple Operators
        parsedData = parsedData.replace('TIMES', '*')
        parsedData = parsedData.replace('PLUS', '+')
        parsedData = parsedData.replace('MINUS', '-')
        parsedData = parsedData.replace('DIVIDED BY', '/')
        parsedData = parsedData.replace('DIVIDEDBY', '/')
        
        # Simple Powers
        parsedData = re.compile('[ ]{1,}SQUARED|[ ]{1,}CUBED').sub(self.__simplePowerReplace, parsedData)

        if parsedData != data:
            parsedData = self.autoFloat(parsedData)
            self.__parsedEquation = self.autoMultiply(parsedData)
            return True
        
        return False
    
    
    def __simplePowerReplace(self, match):
        """Converts "SQUARED" and "CUBED" to their proper exponent representation"""
        
        myString = match.group()
        
        if (myString.find('SQUARED') != -1):
            myString = '**2'
        elif (myString.find('CUBED') != -1):
            myString = '**3'
        
        return myString
    
    
    def __squareRootTextReplace(self, match):
        """Replaces square root references with math.sqrt"""
        
        myString = match.group().replace('SQUARE','')
        myString = myString.replace('ROOT','')
        myString = myString.replace('OF','')
        myString = myString.strip()
        
        myString = 'math.sqrt('+myString+')'
        
        return myString
    

    def autoFloat(self, data):
        """Makes all digits/decimals into floats so we can do proper math on them without auto-rounding"""

        data = re.compile(r'\d+(\.\d+)?').sub(self.__floatReplace, data)
        
        return data
        

    def __floatReplace(self, match):
        """
        This turns our numbers into floats before we eval the equation.
        This is because 4/5 comes out at 0, etc. Python is strongly typed...
        """
        string = 'float('+match.group()+')'
        return string
        
    
    def autoMultiply(self, data):
        """Any back to back parens/floats can be assumed to be multiplication. Adding * operator between them"""
        data = string.replace(data, ')float', ')*float')
        data = string.replace(data, ')(', ')*(')
        
        return data


    def checkForSafeEquationString(self, equation):
        """
        Checks to make sure that the equation doesn't contain any unexpected characters
        
        This is pseudo-sanitization. We just make sure that the string has only "safe" characters
        We do this by removing all expected strings, and seeing if we have nothing left.
        """

        # These are characters or strings that we can use in an equation
        safeStrings = ['math.sqrt', 'float', '(', ')', '*', '+', '-', '/', '.']

        for ss in safeStrings:
            equation = string.replace(equation, ss, '')

        for num in xrange(10):
            equation = string.replace(equation, str(num), '')

        equation = equation.strip()

        return ('' == equation)

        
    def solveEquation(self, equation):
        """Sanitizes and Evaulates the equation to see if it's solve-able"""

        if not self.checkForSafeEquationString(equation):
            return False
        
        try:
            return eval(equation.strip())
        except:
            self.Confidence = 0
            return False
    
        
    def calculateConfidence(self, data):
        """Calculates a confidence rating for this (possible) equation"""
        confidence = 100

        # lowering confidence if we have a phone number
        try:
            if len(data) <= 30 and len(data) >= 7:
                phonenumberutil.parse(data, _check_region=False)
                for char in [c for c in data if c in string.punctuation]:
                    confidence -= 10
        except:
            pass

        # We remove confidence for every token shared with a programming language.
        if (ProgrammingParser in config.enabledModules):
            progParser = ProgrammingParser()
            dataset = progParser.createDataset(data)
            for token in set(progParser.findCommonTokens(dataset)):
                confidence -= 5

        return confidence


    def parse(self, data, **kwargs):
        """Standard parse function for checking if entered string is a mathematical equation"""
        
        # if we just have a number, we know this isn't an equation
        if isNumber(data):
            return
        
        # Doing some initial data cleanup
        cleanData = string.replace(data.upper(), 'X', '*')
        cleanData = string.replace(cleanData, '^', '**')
        cleanData = string.replace(cleanData, 'THE', '')
        cleanData = cleanData.strip()
        
        if len(cleanData) == 0:
            return
        
        # We start with 100% confidence, and then lower our confidence if needed.
        if self.isSimpleEquation(cleanData):
            resultType = "Simple"
        elif self.isTextEquation(cleanData):
            resultType = "Text"
        else:
            return

        # If the equation proves to be solveable, we calculate a confidence and report success
        calculated = self.solveEquation(self.__parsedEquation)
        if calculated:
            yield self.result(resultType, self.calculateConfidence(data), calculated)

