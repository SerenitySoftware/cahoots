from parsers import base
from brain.util import truncateText
import datetime, threading, time, config

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


def bootstrap(silent=False, *args, **kwargs):
    """Bootstraps each parser. Can be used for cache warming, etc."""
    for module in config.enabledModules:
        """If the module overrides the base bootstrap, we output a message about it"""
        if not silent and module.bootstrap != base.BaseParser.bootstrap:
            print ' * '+time.strftime('%X %x %Z')+' * Bootstrapping '+module.__name__

        module.bootstrap();


def parse(dataString, *args, **kwargs):
    """Parses input data and returns a dict of result data"""
    results = []
    threads = []

    # Creating/starting a thread for each parser module
    for module in config.enabledModules:
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