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
    CaselessLiteral, \
    ParseException, \
    Word, \
    originalTextFor, \
    ZeroOrMore, \
    nums, \
    alphas, \
    StringEnd


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
        pre_timedelta_phrases = \
            pre_timedeltas + Word(alphas + nums + " .,;-/'")
        registry.set('DP_pre_timedelta_phrases', pre_timedelta_phrases)

        # <operator> <number> <timescale>
        # plus 5 hours / - 17 days
        post_timedelta_phrases = Or(
            [DateParser.create_post_timedelta_literal(t) for t in time_scales]
        )
        registry.set('DP_post_timedelta_phrases', post_timedelta_phrases)

    @staticmethod
    def create_pre_timedelta_literal(tok):
        """Detects <number> <timescale> <preposition>"""
        delta = originalTextFor(Or([
            Word(nums) +
            ZeroOrMore(',' + Word(nums+',')) +
            ZeroOrMore('.' + Word(nums)),
            CaselessLiteral('an'),
            CaselessLiteral('a')
        ])) + CaselessLiteral(tok) + DateParser.get_preposition_literals()

        delta.setName('pre' + tok).\
            setParseAction(DateParser.generate_pre_timedelta)

        return delta

    @staticmethod
    def generate_pre_timedelta(toks):
        """Generates a timedelta object for a delta-prefix match"""
        minus_prepositions = [
            'until',
            'before',
            'to',
            'from',
        ]

        number, timescale, preposition = toks

        number = DateParser.get_number_value(number)

        if preposition in minus_prepositions:
            number = number * -1

        return DateParser.determine_timescale_delta(timescale, number)

    @staticmethod
    def create_post_timedelta_literal(tok):
        """Detects <plus/minus> <number> <timescale>"""
        delta = Or(
            [CaselessLiteral(t) for t in ['+', '-', 'plus', 'minus']]
        ) + originalTextFor(Or([
            Word(nums) +
            ZeroOrMore(',' + Word(nums+',')) +
            ZeroOrMore('.' + Word(nums)),
            CaselessLiteral('an'),
            CaselessLiteral('a')
        ])) + CaselessLiteral(tok) + StringEnd()

        delta.setName('post' + tok).\
            setParseAction(DateParser.generate_post_timedelta)

        return delta

    @staticmethod
    def generate_post_timedelta(toks):
        """Generates a timedelta object for a delta-suffix match"""
        operator, number, timescale = toks

        number = DateParser.get_number_value(number)

        if operator in ['minus', '-']:
            number = number * -1

        delta = DateParser.determine_timescale_delta(timescale, number)

        return delta

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
    def get_number_value(number):
        """Turns a provided number into a proper float"""
        if number in ['a', 'an']:
            number = 1.0
        else:
            number = \
                float("".join([char for char in number if char in nums+'.']))

        return number

    @staticmethod
    def determine_timescale_delta(timescale, number):
        """Gets a timedelta representing the change desired"""
        if timescale[-1:] != 's':
            timescale += 's'

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

    def __init__(self, config):
        BaseParser.__init__(self, config, "Date", 0)

    @classmethod
    def natural_parse(cls, data):
        """
        Parse out natural-language strings like "yesterday", "next week", etc
        """
        data = data.lower()
        today = datetime.today()

        if data in ['now', 'current time']:
            value = today.now()
        elif data == 'today':
            value = today
        elif data == "tomorrow":
            value = today + timedelta(1)
        elif data == "yesterday":
            value = today + timedelta(-1)
        elif data == "next week":
            value = today + timedelta(7)
        elif data == "last week":
            value = today + timedelta(-7)
        elif data == "next year":
            value = today + timedelta(365)
        elif data == "last year":
            value = today + timedelta(-365)
        else:
            value = False

        return value

    def date_parse(self, data):
        """Uses the dateUtilParser to determine what our date is"""
        parsed_date = self.natural_parse(data)
        if parsed_date:
            return ('Natural', parsed_date)
        else:
            try:
                return ('Standard', dateUtilParser.parse(data))
            except BaseException:
                pass

        return False

    def parse(self, data_string):
        data_string = data_string.strip()

        if len(data_string) < 3 or len(data_string) > 50:
            return

        # Just date detection
        parsed_date = self.date_parse(data_string)
        if parsed_date:
            yield self.result(parsed_date[0], 100, parsed_date[1])
            return

        # Looking for <number> <timescale> <prepositions> <datetime>
        pre_timedelta_phrases = registry.get('DP_pre_timedelta_phrases')
        try:
            pre_delta = pre_timedelta_phrases.parseString(data_string)
        except ParseException:
            pass
        else:
            parsed_date = self.date_parse(pre_delta[1])
            if parsed_date:
                try:
                    yield self.result(
                        "Number Timescale Preposition Date",
                        100,
                        parsed_date[1] + pre_delta[0]
                    )
                except OverflowError:
                    pass
                return

        # Looking for <datetime> <plus/minus> <number> <timescale>
        post_timedelta_phrases = registry.get('DP_post_timedelta_phrases')
        post_deltas = \
            [t for t in post_timedelta_phrases.scanString(data_string)]
        if len(post_deltas) == 1:
            for token, start, _ in post_deltas:
                parsed_date = self.date_parse(data_string[0:start].strip())
                if parsed_date:
                    try:
                        yield self.result(
                            "Date Operator Number Timescale",
                            100,
                            parsed_date[1] + token.pop()
                        )
                    except OverflowError:
                        pass
                    return
