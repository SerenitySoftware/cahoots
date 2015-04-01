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
from SereneRegistry import registry
from cahoots.parsers.base import BaseParser
from cahoots.data import DataHandler
from datetime import timedelta, datetime
import dateutil.parser as dateUtilParser
from pyparsing import\
    Or, \
    OneOrMore, \
    Optional, \
    CaselessLiteral, \
    StringEnd, \
    ParseException, \
    replaceWith, \
    Word, \
    originalTextFor, \
    ZeroOrMore, \
    nums, \
    alphas, printables
import string


class DateParser(BaseParser):
    '''Determines is given data is a date'''

    @staticmethod
    def bootstrap(config):

        time_scales = [
            'microseconds',
            'milliseconds',
            'seconds',
            'minutes',
            'hours',
            'days',
            'weeks',
            'years',
            'microsecond',
            'millisecond',
            'second',
            'minute',
            'hour',
            'day',
            'week',
            'year',
        ]

        # <number> <timescale> <preposition>
        # 3 seconds until / 50 seconds since
        pre_timedeltas = Or(
            [DateParser.create_pre_timedelta_literal(t) for t in time_scales]
        )

        pre_timedelta_phrases = pre_timedeltas + Word(printables)
        registry.set('DP_pre_timedelta_phrases', pre_timedelta_phrases)

    @staticmethod
    def create_pre_timedelta_literal(tok):
        """Converts a value to pyparsing caselessliteral"""
        timedelta = originalTextFor(
            Word(nums) +
            ZeroOrMore(',' + Word(nums+',')) +
            ZeroOrMore('.' + Word(nums))
        ) + CaselessLiteral(tok) + DateParser.get_preposition_literals()

        timedelta.setName(tok).setParseAction(DateParser.generate_timedelta)

        return timedelta

    @staticmethod
    def get_preposition_literals():
        """Generates the prepositions parser and returns it"""
        if registry.test('DP_prepositions'):
            return registry.get('DP_prepositions')

        prepositions = \
            Or([CaselessLiteral(s) for s in DataHandler().get_prepositions()])

        registry.set('DP_prepositions', prepositions)
        return prepositions

    @staticmethod
    def generate_timedelta(toks):
        minus_prepositions = [
            'until',
            'before',
            'to',
            'from',
        ]

        number, timescale, preposition = toks

        number = float("".join([char for char in number if char in nums+'.']))

        if preposition in minus_prepositions:
            number = number * -1

        if timescale == 'microseconds':
            delta = timedelta(microseconds=number)
        elif timescale == 'milliseconds':
            delta = timedelta(milliseconds=number)
        elif timescale == 'seconds':
            delta = timedelta(seconds=number)
        elif timescale == 'minutes':
            delta = timedelta(minutes=number)
        elif timescale == 'hours':
            delta = timedelta(hours=number)
        elif timescale == 'days':
            delta = timedelta(days=number)
        elif timescale == 'weeks':
            delta = timedelta(weeks=number)
        elif timescale == 'years':
            delta = timedelta(days=365*number)
        else:
            delta = timedelta()

        return delta

    @classmethod
    def natural_parse(cls, data_string):
        """
        Parse out natural-language strings like "yesterday", "next week", etc
        """
        data_string = data_string.lower()
        today = datetime.today()

        if data_string == "yesterday":
            return today - timedelta(1)

        if data_string == "tomorrow":
            return today + timedelta(1)

        if data_string == "next week":
            return today + timedelta(days=6-today.weekday())

        if data_string == "last week":
            return today - timedelta(days=8+today.weekday())

        return False

    def __init__(self, config):
        BaseParser.__init__(self, config, "Date", 0)

    def parse(self, data_string):
        data_string = data_string.strip()

        if len(data_string) < 4:
            return

        pre_timedelta_phrases = registry.get('DP_pre_timedelta_phrases')
        pre_delta = pre_timedelta_phrases.parseString(data_string)
        print(pre_delta)

        if pre_delta:
            parsed_date = self.natural_parse(pre_delta[1])
            if parsed_date:
                yield self.result("Date", 100, parsed_date + pre_delta[0])
            else:
                try:
                    parsed_date = dateUtilParser.parse(pre_delta[1])
                    yield self.result("Date", 100, parsed_date + pre_delta[0])
                except (StopIteration, ValueError, OverflowError, TypeError) as e:
                    pass

        '''
        # Checking for other date standards

        punctuation = [c for c in data_string if
                       c in string.punctuation or
                       c in string.whitespace]
        letters = [c for c in data_string if c in string.ascii_letters]
        digits = [c for c in data_string if c in string.digits]

        self.calculate_confidence(
            len(data_string), punctuation, letters, digits
        )

        yield self.result("Date", self.confidence, parsed_date)
        '''
