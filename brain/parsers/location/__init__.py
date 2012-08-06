from brain.parsers.base import BaseParser

class LocationParser(BaseParser):

	def __init__(self):
		self.Type = "Location"
		self.Confidence = 100
	
	def parse(self, data, **kwargs):
		pass