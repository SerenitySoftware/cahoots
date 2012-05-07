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
		data = data.decode('utf-8')
		
		if len(data) != 1:
			return self.result(False)
		
		try:
			ascii_version = ord(data)
		except UnicodeEncodeError:
			ascii_version = None
			
		try:
			utf8_version = ord(unicode(data))
		except UnicodeEncodeError:
			utf8_version = None
			
		character_data = {
			"ascii": ascii_version,
			"utf-8": utf8_version
		}
			
		if self.isLetter(data):
			return self.result(True, "Letter", data = character_data)
			
		if self.isPunctuation(data):
			return self.result(True, "Punctuation", data = character_data)
			
		if self.isWhitespace(data):
			return self.result(True, "Whitespace", data = character_data)

		return self.result(False)