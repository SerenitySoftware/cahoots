from base import BaseParser
import re

class NumberParser(BaseParser):

	def __init__(self):
		self.Type = "Number"
		self.Confidence = 10

	def isFloat(self, data):
		try:
			float(data)
			return True
		except ValueError:
			return False

	def isInteger(self, data):
		try:
			int(data)
			return True
		except ValueError:
			return False
			
	def isHex(self, data):
		if data[0] == '#':
			data = data[1:]
			
		try:
			int(data, 16)
			return True
		except ValueError:
			return False
			
	def isBinary(self, data):
		if len(data) < 4:
			return False
		
		if len(data) % 4 != 0:
			return False
			
		for c in data:
			if c != "0" and c != "1":
				return False
				
		return True
		
	def isOctal(self, data):
		try:
			int(data, 8)
			return True
		except ValueError:
			return False
	
	def isRomanNumeral(self, data):
		data = data.upper()
		rgx_roman = re.compile("""^
		   ([M]{0,9})   # thousands
		   ([DCM]*)     # hundreds
		   ([XLC]*)     # tens
		   ([IVX]*)     # units
		   $""", re.VERBOSE)
		
		match = rgx_roman.match(data)
		
		if match:
			return True
			
		return False
	
	def isFraction(self, data):
		if not '/' in data:
			return False
		
		whitespace_split = data.split()
		if len(whitespace_split) > 1:
			for whitespace_section in whitespace_split:
				if not self.parse(whitespace_section.strip()).Matched:
					return False
		else:
			fraction_split = data.split("/")
			
			for split_section in fraction_split:
				if not self.parse(split_section).Matched:
					return False
				
		return True
			
	def parse(self, data, **kwargs):
		if data == "":
			return self.result(False)
			
		if data[0] == "-":
			data = data[1:]

		data = data.replace(",", "")
		
		if data == '':
			return self.result(False)
		
		if self.isFraction(data):
			return self.result(True, "Fraction", 65)
					
		if self.isBinary(data):
			return self.result(True, "Binary", 95)
			
		if self.isInteger(data):
			return self.result(True, "Integer", 80)
			
		if self.isFloat(data):
			return self.result(True, "Decimal", 80)
			
		if self.isOctal(data):
			return self.result(True, "Octal", 80)
			
		if len(data) > 1 and self.isHex(data):
			return self.result(True, "Hexadecimal", 80)
			
		if self.isRomanNumeral(data):
			return self.result(True, "Roman Numeral", 80)
			
		return self.result(False)
	