#import pyparsing
from parsers import number, character, boolean, date, phone, uri, email, place, programming, grammar, measurement, address
import datetime

checks = [
	number.NumberParser,
	character.CharacterParser,
	boolean.BooleanParser,
	date.DateParser,
	phone.PhoneParser,
	uri.URIParser,
	email.EmailParser,
	place.PlaceParser,
	programming.ProgrammingParser,
	grammar.GrammarParser,
	address.AddressParser
]

def parse(dataString, *args, **kwargs):
	match_types = []
	results = []
	
	for module in checks:
		p = module()
		result = p.parse(dataString, **kwargs)
		
		if result.Matched:
			match_types.append(p.Type)
			results.append(result)
			
	matches = sorted(results, key = lambda result: result.Confidence, reverse = True)
	match_count = len(matches)
	query = dataString
	
	return {
		'query': query,
		'date': datetime.datetime.now(),
		'top': matches[0] if len(matches) > 0 else None,
		'results': {
			'count': match_count,
			'types': match_types,
			'matches': matches
		}
	}
	