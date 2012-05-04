from base import BaseParser
import re
#import email
#from email import utils
#from lepl.apps.frc3696 import Email

class EmailParser(BaseParser):

	def __init__(self):
		self.Type = "Email"
		self.Confidence = 50
	
	def parse(self, dataString, **kwargs):
		if '@' not in dataString:
			return self.result(False)
		
		match = re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", dataString)
		if match:
			return self.result(True, "Email Address")
		
		return self.result(False)