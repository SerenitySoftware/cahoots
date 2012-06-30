from exceptions import NotImplementedError
from brain.result import ParseResult, ParseResultMulti

class BaseParser:

	Type = "Base"
	Confidence = 10

	def parse(self, data, *args, **kwargs):
		raise NotImplementedError, "Class must override the parse() method"
		
	def result(self, matched, subtype = "Unknown", Confidence = 0, data = {}):
		if Confidence == 0:
			Confidence = self.Confidence
			
		return ParseResult(matched, self.Type, subtype, Confidence, data)


	def resultMulti(self, resultData):
		'''
		Classes can return multiple results, but have to assemble the object themselves
		Should return a ParseResultMulti object
		'''
		raise NotImplementedError