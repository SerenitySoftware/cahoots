from base import BaseParser


class GrammarParser(BaseParser):

    def __init__(self, config):
        BaseParser.__init__(self, config, "Grammar", 25)

    def parse(self, data, **kwargs):
        pass
