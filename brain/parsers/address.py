from base import BaseParser

class AddressParser(BaseParser):

	def __init__(self):
		self.Type = "Address"
		self.Confidence = 100
	
	def parse(self, data, **kwargs):
			
		return self.result(False)
		