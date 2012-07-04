from base import BaseParser
import string, re

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
		
		if '+' in punctuation or '*' in punctuation:
			if dataString[0] not in ['+','*']:
				return self.result(False)
		
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
		phoneChars = re.compile("""^
           ([\(\)\+\*\-0-9/ ])*
           $""", re.VERBOSE)
		
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
				
				slashPhone = re.compile('[0-9]{3}/[0-9]{7}|\([0-9]{3,4}\)[0-9]{7}');
				
				#if our digits are of a possible right length, and we contain dashes or whitespace, probably a phone number
				if '-' in punctuation or ' ' in punctuation:
					self.Confidence = 90
					
				elif slashPhone.match(dataString):
					self.Confidence = 80
				
				# could be a phone number, probably an integer or something along those lines
				else:
					self.Confidence = 15
								
		return self.result(True, "Phone Number")

"""
	def format(self, number):
		chunks = re.split('[\.,!\?;\- ]', number)
		format = self.determine_phone_format(chunks)
		
		if not format:
			return '-'.join(chunks)
			
		rendered_phone = ''
		render_format = format[3]
		render_index = 0
		phone_digits = list(''.join(chunks))
		
		for c in list(render_format):
			if c == '#':
				rendered_phone += phone_digits[render_index]
				render_index += 1
			else:
				if c == phone_digits[render_index]:
					render_index += 1
				rendered_phone += c
				
		return {
			'format': render_format,
			'country': format[0],
			'clean': rendered_phone
		}
		
	def determine_phone_format(self, chunks):
		formats = (
			('USA', 1, (
				'###-###-####',
				'1-###-###-####'
			), '+1 (###) ###-####'),
			('Denmark', 45, (
				'##-##-##-##',
				'####-####'
			)),
			('France', 33, (
				'0#-##-##-##-##',
			)),
		)
		
		for country in formats:
			for format in country[2]:
				if self.does_phone_match_format(chunks, format, country[1]):
					return country
		
		return None
		
	def does_phone_match_format(self, phone, format, calling_code):
		format_chunks = format.split("-")
		if len(phone) != len(format_chunks):
			return False
		
		zipped_chunks = zip(phone, format_chunks)
		
		for chunk in zipped_chunks:
			if len(chunk[0]) != len(chunk[1]):
				return False
				
			zipped_numbers = zip(list(chunk[0]), list(chunk[1]))
			
			for num_format in zipped_numbers:
				phone_character = num_format[0]
				format_character = num_format[1]
				
				if not phone_character in string.digits:
					return False
					
				if format_character != '#' and format_character != phone_character:
					return False
		
		return True
"""			