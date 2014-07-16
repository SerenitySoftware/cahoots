import simplejson
from datetime import *
from brain.result import ParseResult

class CahootsEncoder(simplejson.JSONEncoder):
	
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.isoformat()
		elif isinstance(obj, date):
			return obj.isoformat()
		elif isinstance(obj, ParseResult):
			return {
				'type': obj.Type,
				'subtype': obj.Subtype,
				'confidence': obj.Confidence,
				'value': obj.ResultValue,
				'data': obj.Data
			}
			
		return super(CahootsEncoder, self).default(obj)

def encode(data, level = 0, indent = True):
	return simplejson.dumps(data, indent = 4, cls = CahootsEncoder)