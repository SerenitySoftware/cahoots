from base import BaseParser
import string

class CharacterParser(BaseParser):

	def __init__(self):
		self.Type = "Character"
		self.Confidence = 15
	
	def isLetter(self, data):
		if data in string.ascii_letters:
			return True
			
		return False
	
	def isPunctuation(self, data):
		if data in string.punctuation:
			return True
			
		return False
		
	def isWhitespace(self, data):
		if data in string.whitespace:
			return True
			
		return False

	def parse(self, data, **kwargs):
		if len(data) != 1:
			return self.result(False)
			
		if self.isLetter(data):
			return self.result(True, "Letter")
			
		if self.isPunctuation(data):
			return self.result(True, "Punctuation")
			
		if self.isWhitespace(data):
			return self.result(True, "Whitespace")

		return self.result(False)