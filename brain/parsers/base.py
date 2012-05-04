from exceptions import NotImplementedError
from brainiac.brain.result import ParseResult

class BaseParser:

	Type = "Base"
	Confidence = 10

	def parse(self, data, *args, **kwargs):
		raise NotImplementedError, "Class must override the parse() method"
		
	def result(self, matched, subtype = "Unknown", Confidence = 0, data = {}):
		if Confidence == 0:
			Confidence = self.Confidence
			
		return ParseResult(matched, self.Type, subtype, Confidence, data)