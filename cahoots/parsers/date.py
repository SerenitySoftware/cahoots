from base import BaseParser
from datetime import date, timedelta
import dateutil.parser as dateUtilParser
import string


class DateParser(BaseParser):

    def __init__(self):
        self.Type = "Date"
        self.Confidence = 0
        
    def naturalParse(self, dataString):
        """parse out natural-language strings like "yesterday", "next week", etc"""
        dataString = dataString.lower()
        today = date.today()
        
        if dataString == "yesterday":
            return today - timedelta(1)
        
        if dataString == "tomorrow":
            return today + timedelta(1)
            
        if dataString == "next week":
            return today + timedelta(days = 6 - today.weekday())
            
        if dataString == "last week":
            return today - timedelta(days = 8 + today.weekday())
        
        return False
        

    def parse(self, dataString, **kwargs):
        punctuation = [c for c in dataString if c in string.punctuation or c in string.whitespace]
        letters = [c for c in dataString if c in string.letters]
        digits = [c for c in dataString if c in string.digits]
        
        dsLength = len(dataString)


        if dsLength < 4:
            return


        # Checking for a natural language date
        parsedDate = self.naturalParse(dataString)
        
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
            parsedDate = dateUtilParser.parse(dataString)

            if dsLength <= 4:
                self.Confidence += 10
            elif dsLength <= 7:
                self.Confidence += 40
            else:
                self.Confidence += 80

            self.Confidence = int(round(float(self.Confidence)*confidenceNormalizer))

            yield self.result("Date", self.Confidence, parsedDate)
        except:
            pass