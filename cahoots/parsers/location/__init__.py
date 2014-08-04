from cahoots.parsers.base import BaseParser


class LocationParser(BaseParser):

    def __init__(self, config):
        BaseParser.__init__(self, config, "Location", 100)

    def parse(self, data, **kwargs):
        pass
