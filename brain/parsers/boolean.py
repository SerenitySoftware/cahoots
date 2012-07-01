from base import BaseParser

class BooleanParser(BaseParser):

	def __init__(self):
		self.Type = "Boolean"
	
	def parse(self, data, **kwargs):
		data = data.lower()
		
		if data in ["true", "false", "yes", "no"]:
			return self.result(True, "Boolean", 95)
			
		if data in ["yep", "yup", "nope"]:
			return self.result(True, "Boolean", 80)
			
		if data in ["1", "0", "t", "f", "one", "zero"]:
			return self.result(True, "Boolean", 40)
			
		return self.result(False)
