from base import BaseParser
import re

class EmailParser(BaseParser):

	def __init__(self):
		self.Type = "Email"
		self.Confidence = 100


	def matchesEmailPattern(self, data):
		"""Checking if the data is an email address"""
		return re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", data)
	

	def parse(self, dataString, **kwargs):
		if '@' not in dataString:
			return
		
		if self.matchesEmailPattern(dataString):
			yield self.result("Email Address", self.Confidence)