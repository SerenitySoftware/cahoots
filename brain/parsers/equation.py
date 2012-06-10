from base import BaseParser
import re
import string
import math


class EquationParser(BaseParser):
    """
    brainiac.brain.parsers.equation
    parser to identify and solve some mathematical equations
    """


    parsedEquation = None
    """ After we've processed the input string from the user, this var will contain the assembled result """


    def __init__(self):
        self.Type = "Equation"
        self.Confidence = 0
    
    
    def isSimpleEquation(self, data):
        """ Seeing if our string only has symbols found in simple math equations """

        rgx = re.compile("""^
           ([()*.\-+0-9^/ ])*
           $""", re.VERBOSE)
           
        match = rgx.match(data)
        
        if match:
            data = self.autoFloat(data)
            self.parsedEquation = self.autoMultiply(data)
            return True
            
        return False
    
    
    def isTextEquation(self, data):
        """ Searching for specific textual markers that can be converted into mathematical operators """
        
        # SQUARE ROOTS
        parsedData = re.compile('SQUARE[ ]{1,}ROOT[ ]{1,}OF[ ]{1,}\d+(\.\d+)?').sub(self.squareRootTextReplace, data)
        
        # Simple Operators
        parsedData = parsedData.replace('TIMES', '*')
        parsedData = parsedData.replace('PLUS', '+')
        parsedData = parsedData.replace('MINUS', '-')
        parsedData = parsedData.replace('DIVIDED BY', '/')
        parsedData = parsedData.replace('DIVIDEDBY', '/')
        
        # Simple Powers
        parsedData = re.compile('[ ]{1,}SQUARED|[ ]{1,}CUBED').sub(self.simplePowerReplace, parsedData)
        
        if parsedData != data:
            parsedData = self.autoFloat(parsedData)
            self.parsedEquation = self.autoMultiply(parsedData)
            return True
        
        return False
    
    
    def simplePowerReplace(self, match):
        """ Converts "SQUARED" and "CUBED" to their proper exponent representation """
        
        myString = match.group()
        
        if (myString.find('SQUARED') != -1):
            myString = '**2'
        elif (myString.find('CUBED') != -1):
            myString = '**3'
        
        return myString
    
    
    def squareRootTextReplace(self, match):
        """ Replaces square root references with math.sqrt """
        
        myString = match.group().replace('SQUARE','')
        myString = myString.replace('ROOT','')
        myString = myString.replace('OF','')
        myString = myString.strip()
        
        myString = 'math.sqrt('+myString+')'
        
        return myString
    

    def autoFloat(self, data):
        """ Makes all digits/decimals into floats so we can do proper math on them without auto-rounding """

        data = re.compile(r'\d+(\.\d+)?').sub(self.floatReplace, data)
        
        return data
        

    def floatReplace(self, match):
        """
        This turns our numbers into floats before we eval the equation.
        This is because 4/5 comes out at 0, etc. Python autorounds...
        """
        string = 'float('+match.group()+')'
        return string
        
    
    def autoMultiply(self, data):
        """ Any back to back parens/floats can be assumed to be multiplication. Adding * operator between them """
        data = string.replace(data, ')float', ')*float')
        data = string.replace(data, ')(', ')*(')
        
        return data


    def checkForSafeEquationString(self):
        """
        Checks to make sure that the equation doesn't contain any unexpected characters
        
        This is pseudo-sanitization. We just make sure that the string has only "safe" characters
        We do this by removing all expected strings, and seeing if we have nothing left.
        """
        equation = self.parsedEquation

        # These are characters or strings that we can use in an equation
        safeStrings = ['math.sqrt', 'float', '(', ')', '*', '+', '-', '/', '.']

        for char in safeStrings:
            equation = string.replace(equation, char, '')

        for num in range(0, 9):
            equation = string.replace(equation, str(num), '')

        equation = equation.strip()

        return ('' == equation)

        
    def solveEquation(self):
        """ Evaulates the equation to see if it's solve-able """

        if not self.checkForSafeEquationString():
            return False
        
        try:
            return eval(self.parsedEquation.strip())
        except:
            self.Confidence = 0
            return False
    
    
    def parse(self, data, **kwargs):
        """ Standard parse function for checking if entered string is a mathematical equation """
        
        # Doing some initial data cleanup
        cleanData = string.replace(data.upper(), 'X', '*')
        cleanData = string.replace(cleanData, '^', '**')
        cleanData = string.replace(cleanData, 'THE', '')
        cleanData = cleanData.strip()
        
        # if we just have a digit, we know this isn't an equation
        if (cleanData.isdigit()):
            return self.result(False);
        
        likely = False
        
        if self.isSimpleEquation(cleanData):
            resultType = "Simple"
            likely = True
        
        if self.isTextEquation(cleanData):
            resultType = "Text"
            likely = True
        
        if likely:
            calculated = self.solveEquation()
            if calculated:
                return self.result(True, resultType, 75, calculated)

        return self.result(False)
        