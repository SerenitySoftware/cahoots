from parsers.base import BaseParser
from cahoots.util import truncateText
from config import BaseConfig
import datetime
import threading
import time
import inspect


class ParserThread (threading.Thread):
    """Represents a thread that will handle one parser parsing request"""
    config = None
    data_string = None
    kwargs = None
    results = []

    def __init__(self, config, module, data_string, **kwargs):
        self.config = config
        self.thread_id = module
        self.data_string = data_string
        self.kwargs = kwargs
        threading.Thread.__init__(self)

    def run(self):
        parser = self.thread_id(self.config)
        self.results = parser.parse(self.data_string, **self.kwargs) or []


class CahootsParser:

    Config = None

    """
    The 'config' variable, if set, needs to be a class that extends
    BaseConfig, or an instance of a class that does.
    In the case that it's a class, we will instantiate the class.
    """
    def __init__(self, config=None, bootstrap=True):

        if config is not None:
            if inspect.isclass(config) and issubclass(config, BaseConfig):
                self.Config = config()
            elif isinstance(config, BaseConfig):
                self.Config = config

        # Config fallback
        if self.Config is None:
            self.Config = BaseConfig()

        """
        This bootstraps our parsing system and
        gets all modules ready for parsing.
        """
        if bootstrap:
            self.bootstrap()

    def bootstrap(self):
        """Bootstraps each parser. Can be used for cache warming, etc."""
        for module in self.Config.enabledModules:
            """
            If the module overrides the base bootstrap,
            we output a message about it
            """
            if self.Config.debug\
               and module.bootstrap != BaseParser.bootstrap:
                print ' * ' + time.strftime('%X %x %Z') +\
                      ' * Bootstrapping '+module.__name__

            module.bootstrap(self.Config)

    def parse(self, data_string, *args, **kwargs):
        """Parses input data and returns a dict of result data"""

        results = []
        threads = []

        # Creating/starting a thread for each parser module
        for module in self.Config.enabledModules:
            thread = ParserThread(self.Config, module, data_string, **kwargs)
            thread.start()
            threads.append(thread)

        # Synchronizing/finishing parser threads
        for t in threads:
            t.join()

        # The threads are done, let's get the results out of them
        for th in threads:
            results.extend(th.results)

        match_types = list(set([result.Type for result in results]))
        matches = sorted(
            results,
            key=lambda result: result.confidence,
            reverse=True
        )
        match_count = len(matches)
        query = data_string

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
