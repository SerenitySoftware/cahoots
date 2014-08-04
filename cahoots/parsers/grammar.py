from base import BaseParser

class GrammarParser(BaseParser):

    def __init__(self):
        self.Type = "Grammar"
        self.Confidence = 25

    def parse(self, dataString, **kwargs):
        pass