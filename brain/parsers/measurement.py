from base import BaseParser
from number import NumberParser
import itertools

class MeasurementParser(BaseParser):

	def __init__(self):
		self.Type = "Measurement"
		self.Confidence = 50

	def derive_splits(self, data):
		if not ' ' in data:
			yield ('', data)
			return
		
		split_index = len(data)
		while True:
			split_index = data.rfind(' ', 0, split_index - 1)
			if split_index == -1:
				return
				
			yield (data[0:split_index - 1], data[split_index + 1:])
		
	def parse(self, dataString, **kwargs):
		number_parser = NumberParser()
		checked_unit = None
		
		for num, unit in self.derive_splits(dataString):
			result = number_parser.parse(num)
			if result.Matched:
				unit_part = unit
				break
				
		if not checked_unit:
			return self.result(False)
			
		#try:
			#unit = Measurement.objects.get(Q(Singular__iequal = checked_unit) | Q(Plural__iequal = checked_unit))
		#	return self.result(True, "Unit")
		#except Measurement.DoesNotExist:
		#	return self.result(False)
			
	
		return self.result(False)