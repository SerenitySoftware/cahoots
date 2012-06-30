from parsers import address, base, boolean, character, date, email, equation, grammar, measurement, number, phone, place, programming, uri
from brain.result import ParseResultMulti
import datetime
import threading

# These are all the parser modules we want to test against
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
    address.AddressParser,
    equation.EquationParser,
]


class ParserThread (threading.Thread):
    """
    Represents a thread that will handle one parser parsing request
    """

    parser = None
    dataString = None
    kwargs = None
    result = None

    def __init__(self, module, dataString, **kwargs):
        self.threadId = module
        self.dataString = dataString
        self.kwargs = kwargs
        threading.Thread.__init__(self)

    def run(self):
        self.parser = self.threadId()
        self.result = self.parser.parse(self.dataString, **self.kwargs)


def parse(dataString, *args, **kwargs):
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
    for t in [th for th in threads if th.result and (isinstance(th.result, ParseResultMulti) or th.result.Matched)]:
        match_types.append(t.parser.Type)
        
        if isinstance(t.result, ParseResultMulti):
            # Getting the multiple results out of a ParseResultMulti object 
            for res in [r for r in t.result.results if r.Matched]:
                results.append(res)
        else:
            # Single Result
            results.append(t.result)


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
    