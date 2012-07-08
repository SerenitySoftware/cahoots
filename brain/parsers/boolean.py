from base import BaseParser

class BooleanParser(BaseParser):

	strongTrue = ["true", "yes"]
	mediumTrue = ["yep", "yup"]
	weakTrue = ["1", "t", "one"]

	strongFalse = ["false", "no"]
	mediumFalse = ["nope"]
	weakFalse = ["0", "f", "zero"]


	def __init__(self):
		self.Type = "Boolean"


	def isTrue(self, data):
		"""Checks if a value is true"""
		if data in self.strongTrue:
			return 100
		elif data in self.mediumTrue:
			return 75
		elif data in self.weakTrue:
			return 50
		return 0


	def isFalse(self, data):
		"""Checks if a value is false"""
		if data in self.strongFalse:
			return 100
		elif data in self.mediumFalse:
			return 75
		elif data in self.weakFalse:
			return 50
		return 0
	

	def parse(self, data, **kwargs):
		data = data.lower()

		# The largest boolean "value" we have is 5 characters long.
		if len(data) > 5:
			return self.result(False)
		
		# Testing for true
		confidence = self.isTrue(data)
		if confidence:
			return self.result(True, "True", confidence, True)

		# Testing for false
		confidence = self.isFalse(data)
		if confidence:
			return self.result(True, "False", confidence, False)
			
		return self.result(False)
