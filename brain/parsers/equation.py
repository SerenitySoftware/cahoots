from base import BaseParser
import re
import string

class EquationParser(BaseParser):
    
    parsedEquation = None


    def __init__(self):
        self.Type = "Equation"
        self.Confidence = 15
    
    
    def isSimpleEquation(self, data):
        
        # Seeing if our string only has symbols found in simple math equations
        rgx = re.compile("""^
           ([\(\)*\-+/0-9\^ ])*
           $""", re.VERBOSE)
           
        match = rgx.match(data)
        
        if match:
            self.Confidence = 50;
            
            self.parsedEquation = data
            
            return True
            
        return False
    
        
    def solveEquation(self):
        
        try:
            result = eval(self.parsedEquation)
        except Exception, e:
            self.Confidence = 0
            return False
        
        self.Confidence = 100
        
        return result
    
    
    def parse(self, data, **kwargs):
        
        # Replacing common math symbols with their python alternatives
        cleanData = string.replace(data.upper(), 'X', '*')
        cleanData = string.replace(cleanData, '^', '**')
        
        solved = False
        
        if self.isSimpleEquation(cleanData):
            resultType = "Simple Equation"
            solved = True
        
        if solved:
            result = self.solveEquation()
            
            if result:
                return self.result(True, resultType, 0, result)

        return self.result(False)
        