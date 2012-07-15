from exceptions import NotImplementedError
from brain.result import ParseResult

class BaseParser:

    Type = "Base"
    Confidence = 10

    def parse(self, data, *args, **kwargs):
        """Base parse method"""
        raise NotImplementedError, "Class must override the parse() method"
        
    def result(self, subtype = "Unknown", Confidence = 0, data = {}):
        """Returns a ParseResult object detailing the results of parsing"""
        if Confidence == 0:
            Confidence = self.Confidence
            
        return ParseResult(self.Type, subtype, Confidence, data)