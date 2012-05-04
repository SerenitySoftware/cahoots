from base import BaseParser

class BooleanParser(BaseParser):

	def __init__(self):
		self.Type = "Boolean"
		self.Confidence = 15
	
	def parse(self, data, **kwargs):
		main_booleans = ["true", "false", "yes", "no"]
		ghetto_booleans = ["0", "1"]
		
		data = data.lower()
		
		if data in main_booleans:
			return self.result(True, "Boolean")
			
		if data in ghetto_booleans:
			return self.result(True, "Boolean", 5)
			
		return self.result(False)
		