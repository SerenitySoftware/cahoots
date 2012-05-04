class ParseResult:
	
	Matched = False
	Type = "Unknown"
	Subtype = "Unknown"
	Confidence = 0
	Data = {}
	
	def __init__(self, matched, type = "Unknown", subtype = "Unknown", Confidence = 0, additional_data = {}):
		self.Matched = matched
		self.Type = type
		self.Subtype = subtype
		self.Confidence = Confidence
		self.Data = additional_data