from base import BaseParser
import string
import re

class PhoneParser(BaseParser):

	def __init__(self):
		self.Type = "Phone"
		self.Confidence = 25
			

	def parse(self, dataString, **kwargs):
		dataString = dataString.strip()
		
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
			
		if len(punctuation) >= 1 and (punctuation[0] == ":" or punctuation[0] == "."):
			return self.result(False) # more likely it's an IP address
			
		if len(punctuation) == 0:
			if len(digits) != 7 and len(digits) != 10 and len(digits) != 11:
				self.Confidence = 5 #probably just a regular number
		else:
			if ',' in punctuation:
				self.Confidence = 5
		
		#checking for existence of only known phone number related characters
		phoneChars = re.compile(r'[\(\)\+\*\-0-9 ]*')
		
		if phoneChars.match(dataString):
			
			# if we have these special chars, we know they only behave certain ways
			if '(' in punctuation or ')' in punctuation or '+' in punctuation or '*' in punctuation:
				
				# these chars would be the ones starting a phone number if we found special chars
				if dataString[0] not in ['+','*','1','(']:
					return self.result(False)
					
				# Starts with 1, but still contains +/* = fail
				if dataString[0] == '1':
					if '+' in punctuation or '*' in punctuation:
						return self.result(False)
				
			# These are the valid lengths for phone number digits
			# some intl phone numbers have 12/13 digits
			if len(digits) in [7,10,11,12,13]:
				
				#if our digits are of a possible right length, and we contain dashes or whitespace, probably a phone number
				if '-' in punctuation or ' ' in punctuation:
					self.Confidence = 90
				
				# could be a phone number, probably an integer or something along those lines
				else:
					self.Confidence = 15
				
					
				
		return self.result(True, "Phone Number")