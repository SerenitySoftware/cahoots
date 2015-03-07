from base import BaseParser
from datetime import date, timedelta
import dateutil.parser as dateUtilParser
import string


class DateParser(BaseParser):

    def __init__(self, config):
        BaseParser.__init__(self, config, "Date", 0)

    def naturalParse(self, data_string):
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

    def parse(self, data_string, **kwargs):
        punctuation = [c for c in data_string if
                       c in string.punctuation or
                       c in string.whitespace]
        letters = [c for c in data_string if c in string.letters]
        digits = [c for c in data_string if c in string.digits]

        dsLength = len(data_string)

        if dsLength < 4:
            return

        # Checking for a natural language date
        parsedDate = self.naturalParse(data_string)

        if parsedDate:
            yield self.result("Date", 100, parsedDate)
            return

        # we will use this to adjust the final confidence score
        confidenceNormalizer = 1.0

        if dsLength > 4:
            confidenceNormalizer *= 1.05

        if len(punctuation) <= 1:
            confidenceNormalizer *= 1.05

        if '/' in punctuation and punctuation.count('/') < 3:
            confidenceNormalizer *= (1.0 + (.05 * punctuation.count('/')))

        if len(letters) == 0 and len(digits) < 4:
            confidenceNormalizer *= 0.5

        try:
            parsedDate = dateUtilParser.parse(data_string)

            if dsLength == 4:
                self.confidence += 10
            elif dsLength <= 7:
                self.confidence += 40
            else:
                self.confidence += 80

            self.confidence = int(
                round(float(self.confidence)*confidenceNormalizer)
            )

            yield self.result("Date", self.confidence, parsedDate)
        except:
            pass
