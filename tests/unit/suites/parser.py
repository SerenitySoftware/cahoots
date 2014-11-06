from cahoots.parser import ParserThread
from cahoots.parsers.base import BaseParser
from tests.unit.config import TestConfig
import unittest

class FakeModule(BaseParser):

    def __init__(self, config):
        BaseParser.__init__(self, config, "Fake")

    def parse(self, data, **kwargs):
        yield self.result("Subtype", 200, "foo")


class parserThreadTests(unittest.TestCase):

    parserThread = None

    def setUp(self):
        self.parserThread = ParserThread(TestConfig, FakeModule, 'datastring')