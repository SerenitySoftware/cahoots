from parsers import base, boolean, character, date, email, equation, grammar, location, measurement, name, number, phone, programming, uri
from brain.util import truncateText
import datetime, threading

# These are all the parser modules we want to test against
checks = [
    name.NameParser,
    number.NumberParser,
    character.CharacterParser,
    boolean.BooleanParser,
    date.DateParser,
    phone.PhoneParser,
    uri.URIParser,
    email.EmailParser,
    programming.ProgrammingParser,
    grammar.GrammarParser,
    location.LocationParser,
    equation.EquationParser,
    measurement.MeasurementParser
]

class ParserThread (threading.Thread):
    """Represents a thread that will handle one parser parsing request"""

    parser = None
    dataString = None
    kwargs = None
    results = []

    def __init__(self, module, dataString, **kwargs):
        self.threadId = module
        self.dataString = dataString
        self.kwargs = kwargs
        threading.Thread.__init__(self)

    def run(self):
        self.parser = self.threadId()
        self.results = self.parser.parse(self.dataString, **self.kwargs) or []


def parse(dataString, *args, **kwargs):
    """Parses input data and returns a dict of result data"""
    match_types = []
    results = []
    threads = []

    # Creating/starting a thread for each parser module
    for module in checks:
        thread = ParserThread(module, dataString, **kwargs)
        thread.start()
        threads.append(thread)

    # Sychronizing/finishing parser threads
    for t in threads:
        t.join()

    # The threads are done, let's get the results out of them
    for th in threads:
        results.extend(th.results)

    match_types = list(set([result.Type for result in results]))
    matches = sorted(results, key = lambda result: result.Confidence, reverse = True)
    match_count = len(matches)
    query = dataString
    
    return {
        'query': truncateText(query),
        'date': datetime.datetime.now(),
        'top': matches[0] if len(matches) > 0 else None,
        'results': {
            'count': match_count,
            'types': match_types,
            'matches': matches
        }
    }