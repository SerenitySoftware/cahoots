from base import BaseParser

class ProgrammingParser(BaseParser):
	
	def __init__(self):
		self.Type = "Programming"
		self.Confidence = 40
		
	def parse(self, dataString, **kwargs):
		return self.result(False)