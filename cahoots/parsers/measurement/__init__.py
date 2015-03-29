"""
The MIT License (MIT)

Copyright (c) Serenity Software, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from pyparsing import \
    Word, \
    nums, \
    CaselessLiteral, \
    Or, \
    ZeroOrMore, \
    originalTextFor, \
    Optional, \
    alphas
from cahoots.parsers.base import BaseParser
from SereneRegistry import registry
from cahoots.data import DataHandler
import os
import glob
import yaml


class MeasurementParser(BaseParser):
    """
    to be used to determine if this is an area
    described using "3 square miles" etc
    """

    @staticmethod
    def bootstrap(config):
        """
        Loads unit lists for use in this instance of the measurement parser
        """
        units = {}
        systems = {}
        prepositions = DataHandler().get_prepositions()

        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "units/*.yaml")

        for file_path in glob.glob(path):
            unit_file = open(file_path, 'r')
            unit_type = yaml.load(unit_file)
            for unit in unit_type['keywords']:
                units[unit] = unit_type['id']
            systems[unit_type['id']] = \
                (unit_type['system'], unit_type['type'])

        preposition_parser = \
            Or([CaselessLiteral(s) for s in prepositions]) + Word(alphas)

        measurement_parser = \
            originalTextFor(
                Word(nums) +
                ZeroOrMore(',' + Word(nums+',')) +
                ZeroOrMore('.' + Word(nums)) +
                ZeroOrMore(Word(nums) + '/' + Word(nums))
            ) + \
            Or([CaselessLiteral(s) for s in units.keys()]) + \
            Optional(originalTextFor(preposition_parser))

        registry.set('MP_units', units)
        registry.set('MP_systems', systems)
        registry.set('MP_preposition_parser', preposition_parser)
        registry.set('MP_measurement_parser', measurement_parser)

    def __init__(self, config):
        BaseParser.__init__(self, config, "Measurement", 100)
        self.units = registry.get('MP_units')
        self.systems = registry.get('MP_systems')
        self.preposition_parser = registry.get('MP_preposition_parser')
        self.measurement_parser = registry.get('MP_measurement_parser')

    def prepare_match(self, result):
        """sets up value and subtype data"""
        amount = \
            result.pop(0).strip() if result[0] is not None else result.pop(0)
        value = {
            'amount': amount,
            'unit': result.pop(0),
            'subject': result.pop(0) if len(result) > 0 else None,
        }

        if value['subject']:
            value['subject'] = \
                self.preposition_parser.parseString(value['subject'])[1]

        system = self.systems[self.units[value['unit']]]
        subtype = system[0] + ' ' + system[1]

        return subtype, value

    def parse(self, data):
        matches = self.measurement_parser.searchString(data).asList()

        for match in matches:
            subtype, value = self.prepare_match(match)
            yield self.result(subtype, self.confidence, value)
            self.confidence -= 5

        if not matches:
            data = data.strip()
            if data in self.units:
                subtype, value = self.prepare_match([None, data])
                yield self.result(subtype, 100, value)
