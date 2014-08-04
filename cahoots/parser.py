from parsers import base
from cahoots.util import truncateText
from config import BaseConfig
from SereneRegistry import registry
import datetime, threading, time


class ParserThread (threading.Thread):
    """Represents a thread that will handle one parser parsing request"""

    dataString = None
    kwargs = None
    results = []

    def __init__(self, module, dataString, **kwargs):
        self.threadId = module
        self.dataString = dataString
        self.kwargs = kwargs
        threading.Thread.__init__(self)

    def run(self):
        parser = self.threadId()
        self.results = parser.parse(self.dataString, **self.kwargs) or []


class CahootsParser:

    config = None

    def __init__(self, config=None):
        if config != None:
            self.config = config
        else:
            self.config = BaseConfig

        # this will be used in lots of places.
        registry.set('Config', self.config)


    def bootstrap(self):
        """Bootstraps each parser. Can be used for cache warming, etc."""
        for module in self.config.enabledModules:
            """If the module overrides the base bootstrap, we output a message about it"""
            if self.config.debug and module.bootstrap != base.BaseParser.bootstrap:
                print ' * '+time.strftime('%X %x %Z')+' * Bootstrapping '+module.__name__

            module.bootstrap()


    def parse(self, dataString, *args, **kwargs):
        """Parses input data and returns a dict of result data"""

        results = []
        threads = []

        # Creating/starting a thread for each parser module
        for module in self.config.enabledModules:
            thread = ParserThread(module, dataString, **kwargs)
            thread.start()
            threads.append(thread)

        # Synchronizing/finishing parser threads
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