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
from cahoots.parsers.base import BaseParser
from datetime import date, timedelta
import dateutil.parser as dateUtilParser
import string


class DateParser(BaseParser):
    '''Determines is given data is a date'''

    def __init__(self, config):
        BaseParser.__init__(self, config, "Date", 0)

    @classmethod
    def natural_parse(cls, data_string):
        """
        Parse out natural-language strings like "yesterday", "next week", etc
        """
        data_string = data_string.lower()
        today = date.today()

        if data_string == "yesterday":
            return today - timedelta(1)

        if data_string == "tomorrow":
            return today + timedelta(1)

        if data_string == "next week":
            return today + timedelta(days=6-today.weekday())

        if data_string == "last week":
            return today - timedelta(days=8+today.weekday())

        return False

    @classmethod
    def confidence_normalizer(cls, ds_length, punctuation, letters, digits):
        """Generates a confidence normalizer for use in calculating conf"""
        normalizer = 1.0

        if ds_length > 4:
            normalizer *= 1.05

        if len(punctuation) <= 1:
            normalizer *= 1.05

        if '/' in punctuation and punctuation.count('/') < 3:
            normalizer *= (1.0 + (.05 * punctuation.count('/')))

        if len(letters) == 0 and len(digits) < 4:
            normalizer *= 0.5

        return normalizer

    def calculate_confidence(self, ds_length, punctuation, letters, digits):
        """Looks at various factors to see how sure we are this is a date"""
        if ds_length == 4:
            self.confidence += 10
        elif ds_length <= 7:
            self.confidence += 40
        else:
            self.confidence += 80

        self.confidence = int(
            round(
                float(self.confidence) *
                self.confidence_normalizer(
                    ds_length, punctuation, letters, digits
                )
            )
        )

    def parse(self, data_string):
        data_string = data_string.strip()

        if len(data_string) < 4:
            return

        # Checking for a natural language date
        parsed_date = self.natural_parse(data_string)
        if parsed_date:
            yield self.result("Date", 100, parsed_date)
            return

        # Checking for other date standards
        try:
            parsed_date = dateUtilParser.parse(data_string)
        except (StopIteration, ValueError, OverflowError, TypeError):
            return

        punctuation = [c for c in data_string if
                       c in string.punctuation or
                       c in string.whitespace]
        letters = [c for c in data_string if c in string.letters]
        digits = [c for c in data_string if c in string.digits]

        self.calculate_confidence(
            len(data_string), punctuation, letters, digits
        )

        yield self.result("Date", self.confidence, parsed_date)
