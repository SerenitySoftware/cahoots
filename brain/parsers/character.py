from base import BaseParser
from boolean import BooleanParser
import string

class CharacterParser(BaseParser):

	def __init__(self):
		self.Type = "Character"
		self.Confidence = 25
	
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
			
		characterData = {
			"ascii": ascii_version,
			"utf-8": utf8_version
		}

		# If this character doesn't evaluate as a boolean, we're positive
		# it's a character if it passes one of the specific evaulations.
		bp = BooleanParser()
		if not bp.isTrue(data) and not bp.isFalse(data):
			self.Confidence = 100
			
		if self.isLetter(data):
			return self.result(True, "Letter", data = characterData)
			
		if self.isPunctuation(data):
			return self.result(True, "Punctuation", data = characterData)
			
		if self.isWhitespace(data):
			return self.result(True, "Whitespace", data = characterData)

		return self.result(False)