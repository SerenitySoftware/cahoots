from base import BaseParser
from datetime import datetime, date, time, timedelta
import calendar
from dateutil.parser import parser as dateparser
import string


class DateParser(BaseParser):

	def __init__(self):
		self.Type = "Date"
		self.Confidence = 50
		
	#parse out natural-language strings like "yesterday", "next week", etc
	def naturalParse(self, dataString):
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
			
		#if dataString == "next month":
		#	days_in_month = calendar.monthrange(today.year, today.month)[1]
		#	return today - timedelta(days = today.day) + timedelta(days = days_in_month + 1)
			
		return False
		
	def parse(self, dataString, **kwargs):
		punctuation = [c for c in dataString if c in string.punctuation or c in string.whitespace]
		letters = [c for c in dataString if c in string.letters]
		
		if len(dataString) < 4:
			return self.result(False)
			
		if len(dataString) == 4:
			self.Confidence = 5
			
		if len(punctuation) <= 1:
			self.Confidence = 5
			
		if '/' in punctuation and punctuation.count('/') == 1:
			self.Confidence = 5
			
		parsedDate = self.naturalParse(dataString)
		
		if parsedDate:
			return self.result(True, "Date", Confidence = 50, data = parsedDate)
		
		try:
			parser = dateparser()
			parsedDate = parser.parse(dataString)
			return self.result(True, "Date", data = parsedDate)
		except:
			pass
		
		return self.result(False)