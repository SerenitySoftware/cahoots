class ParseResult:
	"""Represents a single result from the parsing process"""
	
	Type = "Unknown"
	Subtype = "Unknown"
	Confidence = 0
	Data = {}
	
	def __init__(self, type = "Unknown", subtype = "Unknown", Confidence = 0, additional_data = {}):
		self.Type = type
		self.Subtype = subtype
		self.Confidence = Confidence
		self.Data = additional_data
