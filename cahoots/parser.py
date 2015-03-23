"""
The MIT License (MIT)

Copyright (c) Serenity Software, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from cahoots.parsers.base import BaseParser
from cahoots.util import truncate_text
from cahoots.config import BaseConfig
import datetime
import threading
import time
import inspect


class ParserThread(threading.Thread):
    """Represents a thread that will handle one parser parsing request"""
    config = None
    data_string = None
    results = []

    def __init__(self, config, module, data_string):
        self.config = config
        self.thread_id = module
        self.data_string = data_string
        threading.Thread.__init__(self)

    def run(self):
        parser = self.thread_id(self.config)
        self.results = parser.parse(self.data_string) or []


class CahootsParser(object):
    '''Kicks off the parsing process'''

    config = None

    # The 'config' variable, if set, needs to be a class that extends
    # BaseConfig, or an instance of a class that does.
    # In the case that it's a class, we will instantiate the class.
    def __init__(self, config=None, bootstrap=False):

        if config is not None:
            if inspect.isclass(config) and issubclass(config, BaseConfig):
                self.config = config()
            elif isinstance(config, BaseConfig):
                self.config = config

        # Config fallback
        if self.config is None:
            self.config = BaseConfig()

        # This bootstraps our parsing system and
        # gets all modules ready for parsing.
        if bootstrap:
            self.bootstrap(self.config)

    @classmethod
    def bootstrap(cls, config):
        """Bootstraps each parser. Can be used for cache warming, etc."""
        for module in config.enabledModules:
            # If the module overrides the base bootstrap,
            # we output a message about it
            if module.bootstrap != BaseParser.bootstrap and config.debug:
                print ' * ' + time.strftime('%X %x %Z') +\
                      ' * Bootstrapping '+module.__name__

            module.bootstrap(config)

    def parse(self, data_string):
        """Parses input data and returns a dict of result data"""

        start_time = time.time()
        results = []
        threads = []

        # Creating/starting a thread for each parser module
        for module in self.config.enabledModules:
            thread = ParserThread(self.config, module, data_string)
            thread.start()
            threads.append(thread)

        # Synchronizing/finishing parser threads
        for thr in threads:
            thr.join()

        # The threads are done, let's get the results out of them
        for thr in threads:
            results.extend(thr.results)

        match_types = list(set([result.type for result in results]))
        matches = sorted(
            results,
            key=lambda result: result.confidence,
            reverse=True
        )
        match_count = len(matches)
        query = data_string

        return {
            'query': truncate_text(query),
            'date': datetime.datetime.now(),
            'execution_seconds': time.time() - start_time,
            'top': matches[0] if len(matches) > 0 else None,
            'results': {
                'count': match_count,
                'types': match_types,
                'matches': matches
            }
        }
