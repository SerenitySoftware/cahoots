from exceptions import NotImplementedError
from brain.result import ParseResult

class BaseParser:

    Type = "Base"
    Confidence = 10

    def parse(self, data, *args, **kwargs):
        """Base parse method"""
        raise NotImplementedError, "Class must override the parse() method"
        
    def result(self, subtype = "Unknown", confidence = 0, value = None, data = {}):
        """Returns a ParseResult object detailing the results of parsing"""
        if confidence == 0:
            confidence = self.Confidence
            
        return ParseResult(type=self.Type, subtype=subtype, confidence=confidence, value=value, additional_data=data)