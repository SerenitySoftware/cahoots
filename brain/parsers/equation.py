from base import BaseParser
import re
import string

class EquationParser(BaseParser):
    
    parsedEquation = None


    def __init__(self):
        self.Type = "Equation"
        self.Confidence = 0
    
    
    def isSimpleEquation(self, data):
        
        # Seeing if our string only has symbols found in simple math equations
        rgx = re.compile('([\(\)\*\-+0-9\^\/ ])*')
           
        match = rgx.match(data)
        
        if match:
            self.Confidence = 25
            self.parsedEquation = data
            return True
            
        return False
    
        
    def solveEquation(self):
        
        try:
            result = eval(self.parsedEquation)
        except Exception, e:
            self.Confidence = 0
            return False
        
        return result
    
    
    def parse(self, data, **kwargs):
        
        # Replacing common math symbols with their python alternatives
        cleanData = string.replace(data.upper(), 'X', '*')
        cleanData = string.replace(cleanData, '^', '**')
        
        # if we just have a digit, we know this isn't an equation
        if (cleanData.isdigit()):
            return self.result(False);
        
        likely = False
        
        if self.isSimpleEquation(cleanData):
            resultType = "Simple Math"
            likely = True
        
        if likely:
            calculated = self.solveEquation()
            if calculated:
                return self.result(True, resultType, 85, calculated)

        return self.result(False)
        