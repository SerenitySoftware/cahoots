from base import BaseParser
from datetime import datetime, date, time, timedelta
import calendar
from dateutil.parser import parser as dateparser
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
		
		dsLength = len(dataString)

		if dsLength < 4:
			return self.result(False)


		# Checking for a natural language date
		parsedDate = self.naturalParse(dataString)
		
		if parsedDate:
			return self.result(True, "Date", 100, parsedDate)

			
		if dsLength > 4:
			self.Confidence += 5
			
		if len(punctuation) <= 1:
			self.Confidence += 5
			
		if '/' in punctuation and punctuation.count('/') < 3:
			self.Confidence += (5 * punctuation.count('/'))
		

		try:
			parser = dateparser()
			parsedDate = parser.parse(dataString)
			
			if dsLength <= 4:
				self.Confidence += 10
			elif dsLength <= 7:
				self.Confidence += 40
			else:
				self.Confidence += 80
			
			return self.result(True, "Date", self.Confidence, parsedDate)
		except:
			pass
		

		return self.result(False)