from exceptions import NotImplementedError
from cahoots.result import ParseResult


class BaseParser(object):

    Config = None
    Type = "Base"
    confidence = 10

    def __init__(self, config, Type="Base", confidence=10, *args, **kwargs):
        self.Config = config
        self.Type = Type
        self.confidence = confidence

    @staticmethod
    def bootstrap(config):
        pass

    def parse(self, data, *args, **kwargs):
        """Base parse method"""
        raise NotImplementedError("Class must override the parse() method")

    def result(self, subtype="Unknown", confidence=0, value=None, data={}):
        """Returns a ParseResult object detailing the results of parsing"""
        if confidence == 0:
            confidence = self.confidence

        return ParseResult(
            type=self.Type,
            subtype=subtype,
            confidence=confidence,
            value=value,
            additional_data=data
        )
