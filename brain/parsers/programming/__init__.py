from brain.parsers.base import BaseParser
from brain.parsers.programming.lexer import ProgrammingLexer
from brain.parsers.programming.bayesian import ProgrammingBayesianClassifier
from brain.result import ParseResult, ParseResultMulti
from brain.util import BrainRegistry
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os, re, glob, yaml

class LanguageFileChangeEventHandler(FileSystemEventHandler):
    """Responsible for reloading language data if the yaml directory changes"""

    # Static Programming Parser Instance
    ppi = None

    def on_any_event(self, event):
        self.ppi.loadTokens(False)


class ProgrammingParser(BaseParser):
    
    __subType = ''
    __success = False

    allKeywords = []
    languageKeywords = {}
    
    
    def __init__(self, initTokens=True):
        self.Type = "Programming"
        self.Confidence = 0

        if initTokens:
            self.initTokens()
        

    def initTokens(self):
        """Loads tokens for use in this instance of the programming parser"""

        # if we have already read in and stored the language stuff in memory, we just pull them out of memory
        if BrainRegistry.test('PPallKeywords') and BrainRegistry.test('PPlanguageKeywords'):
            self.allKeywords = BrainRegistry.get('PPallKeywords')
            self.languageKeywords = BrainRegistry.get('PPlanguageKeywords')
            return

        # Not found....Load it!
        self.loadTokens()


    def loadTokens(self, setupWatcher=True):
        """
        Reloads tokens from the yaml files on disk
        Optionally sets of a watcher for changes of the yaml file directory
        """

        self.allKeywords = []
        self.languageKeywords = {}

        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "languages/*.yaml")

        for filePath in glob.glob(path):
            with open(filePath, 'r') as languageFile:
                language = yaml.load(languageFile)
                self.allKeywords.extend(language['keywords'])
                self.languageKeywords[language['id']] = language

        self.allKeywords = set(self.allKeywords)

        BrainRegistry.set('PPallKeywords', self.allKeywords)
        BrainRegistry.set('PPlanguageKeywords', self.languageKeywords)

        # Launching an observer to watch for changes to the language directory
        if setupWatcher:
            LanguageFileChangeEventHandler.ppi = ProgrammingParser(False)
            event_handler = LanguageFileChangeEventHandler()
            observer = Observer()
            observer.schedule(event_handler, os.path.join(directory, "languages/"))
            observer.start()
    

    # finding common words/phrases in programming languages
    def findCommonTokens(self, dataset):
        return [keyword for keyword in dataset if keyword in self.allKeywords]


    def basicLanguageHeuristic(self, language, languageData, dataset):
        return [keyword for keyword in dataset if keyword in languageData['keywords']]


    def parse(self, data, **kwargs):
        """
        Determines if the data is an example of:
            Java, C, C++, PHP, VB, Python, C#, Javascript, Perl, Ruby, or Actionscript
        """

        dataset = set(re.split('[ ;,{}()\n\t\r]', data.lower()))


        # Step 1: Is this possibly code?
        if not self.findCommonTokens(dataset):
            return self.result(False)
        

        # Step 2: Which languages match, based on keywords alone?
        matchedLanguages = [language for language, languageData in self.languageKeywords.items() if self.basicLanguageHeuristic(language, languageData, dataset)]

        if not matchedLanguages:
            return self.result(False)


        # Step 3: Which languages match, based on a smarter lexer?
        lexer = ProgrammingLexer(matchedLanguages, data.lower())
        lexedLanguages = lexer.lex()

        if not lexedLanguages:
            return self.result(False)

        # Giving ourselves a maximum of 10% confidence addition for lexer detection
        normalizer = 10 / float(max([scr for lexid, scr in lexedLanguages.items()]))
        normalScores = {}

        for langId, score in lexedLanguages.items():
            normalScores[langId] = (normalizer * score)


        #Step 4: Using a Naive Bayes Classifier to pinpoint the best language fits
        classifier = ProgrammingBayesianClassifier()
        bayesLanguages = classifier.classify(data)

        # Pulling some stats out of our bayes results so we can calculate a confidence
        results = [[lid, scr] for lid, scr in bayesLanguages.items() if lid in lexedLanguages]
        scores = [scr for lid, scr in results]
        minScore = min(scores)
        spread = max(scores) - minScore

        '''
        We want to add up to 90% confidence based on the spread from min to max matches
        Math for the actual normalization is explained in a comment below
        '''
        if spread > 90:
            normalizer = 90.00 / spread
        else:
            normalizer = 1.00

        # Normalizing and assembling results
        for langId, score in results:
            '''
            Example:

                minScore = -1700
                score = -1500
                Therefore: score = -1500 + 1700 (200)

                OR

                minScore = -50
                score = -25
                Therefore: score = 25
            '''
            if minScore < -90:
                score = score + (-1 * minScore)
            else:
                score = -1 * score

            '''
            Example:
                spread > 90 example:
                    score = 210
                    spread = 240 (ie: max of -1700 to min of -1940)
                    normalizer = 90 / 240 = 0.375
                    normalized score = 78.75

                spread <= 90 example:
                    score 25
                    spread = 30
                    normalizer = 1
                    normalized score = 25
            '''
            normalScores[langId] += (normalizer * score)


        # We reduce our confidence significantly if the string provided is very short
        normalizer = (min(100, float(len(data))) / 100)
        if (normalizer < 1):
            for langId in normalScores:
                normalScores[langId] = normalScores[langId] * normalizer


        # turning the score into an integer
        for langId in normalScores:
            normalScores[langId] = int(round(normalScores[langId]))

        return self.resultMulti(normalScores)


    def resultMulti(self, resultData):
        """Prepares a ParseResultMulti object containing the programming languages detected"""

        return ParseResultMulti([ParseResult(True, self.Type, self.languageKeywords[langId]['name'], confidence) for langId, confidence in resultData.items()])
