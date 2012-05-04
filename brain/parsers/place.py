from base import BaseParser

class PlaceParser(BaseParser):

	def __init__(self):
		self.Type = "Place"
		self.Confidence = 100

	def parse(self, dataString, **kwargs):
		return self.result(False)