from base import BaseParser
import re
import string
import math

class EquationParser(BaseParser):
    
    # This is our completely parsed equation ready to be solved
    parsedEquation = None

    def __init__(self):
        self.Type = "Equation"
        self.Confidence = 0
    
    
    def isSimpleEquation(self, data):
        
        # Seeing if our string only has symbols found in simple math equations
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
        
        # SQUARE ROOTS
        parsedData = re.compile('SQUARE ROOT OF \d+(\.\d+)?').sub(self.squareRootTextReplace, data)
        
        if parsedData != data:
            parsedData = self.autoFloat(parsedData)
            self.parsedEquation = self.autoMultiply(parsedData)
            return True
        
        return False
    
    
    # replacing square root references with math.sqrt
    def squareRootTextReplace(self, match):
        
        string = match.group().replace('SQUARE ROOT OF','').strip()
        string = 'math.sqrt('+string+')'
        
        return string
    
    
    # making all digits/decimals into floats
    def autoFloat(self, data):
        data = re.compile(r'\d+(\.\d+)?').sub(self.floatReplace, data)
        
        return data
        
    
    # This turns our numbers into floats before we eval the equation.
    # This is because 4/5 comes out at 0, etc. Python autorounds...
    def floatReplace(self, match):
        string= 'float('+match.group()+')'
        return string
        
    
    # Any back to back parens/floats can be assumed to be multiplication
    def autoMultiply(self, data):
        data = string.replace(data, ')float', ')*float')
        data = string.replace(data, ')(', ')*(')
        
        return data
        
        
    def solveEquation(self):
        
        try:
            result = eval(self.parsedEquation.strip())
        except:
            self.Confidence = 0
            return False
        
        return result
    
    
    def parse(self, data, **kwargs):
        
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
        