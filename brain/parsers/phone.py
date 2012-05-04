from base import BaseParser
import string

class PhoneParser(BaseParser):

	def __init__(self):
		self.Type = "Phone"
		self.Confidence = 25
			

	def parse(self, dataString, **kwargs):
		if len(dataString) > 30:
			return self.result(False)
			
		digits = [c for c in dataString if c in string.digits]
		letter_set = set()
		letters = [c for c in dataString if c in string.letters and c not in letter_set and not letter_set.add(c)]
		punctuation = [c for c in dataString if c in string.punctuation or c in string.whitespace]
		
		if len(letters) > 3:
			return self.result(False)
			
		if len(digits) < 7:
			return self.result(False)
			
		if len(digits) < (len(punctuation)  + len(letters)):
			return self.result(False)
			
		if len(punctuation) == 1 and (punctuation[0] == ":" or punctuation[0] == "."):
			return self.result(False) # more likely it's an IP address
			
		if len(punctuation) == 0:
			if len(digits) != 7 and len(digits) != 10 and len(digits) != 11:
				self.Confidence = 5 #probably just a regular number
		else:
			if ',' in punctuation:
				self.Confidence = 5
			
				
		return self.result(True, "Phone Number")