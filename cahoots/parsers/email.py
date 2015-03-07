from base import BaseParser
import re


class EmailParser(BaseParser):

    def __init__(self, config):
        BaseParser.__init__(self, config, "Email", 100)

    def matchesEmailPattern(self, data):
        """Checking if the data is an email address"""
        return re.match(
            "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", data
        )

    def parse(self, data_string, **kwargs):
        if '@' not in data_string:
            return

        if self.matchesEmailPattern(data_string):
            yield self.result("Email Address", self.confidence)
