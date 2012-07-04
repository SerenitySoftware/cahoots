from brain.parsers.base import BaseParser
from brain.parsers.programming.lexer import ProgrammingLexer
from brain.result import ParseResult, ParseResultMulti
from brain.util import BrainRegister
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import re
import glob
import yaml

class LanguageFileChangeEventHandler(FileSystemEventHandler):

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

        # if we have already read in and stored the language stuff in memory, we just pull them out of memory
        if BrainRegister.get('PPallKeywords') and BrainRegister.get('PPlanguageKeywords'):
            self.allKeywords = BrainRegister.get('PPallKeywords')
            self.languageKeywords = BrainRegister.get('PPlanguageKeywords')
            return

        # Not found....Load it!
        self.loadTokens()


    def loadTokens(self, setupWatcher=True):

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

        BrainRegister.set('PPallKeywords', self.allKeywords)
        BrainRegister.set('PPlanguageKeywords', self.languageKeywords)

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


    def bayesClassification(self, language, data):
        return { 'confidence': 100, 'language': language }
    

    def parse(self, data, **kwargs):
        '''
        Determines if the data is an example of:
            Java, C, C++, PHP, VB, Python, C#, Javascript, Perl, Ruby, or Actionscript
        '''
        data = data.lower()
        dataset = set(re.split('[ ;,{}()\n\t\r]', data))


        # Step 1: Is this even code?
        if not self.findCommonTokens(dataset):
            return self.result(False)
        
        # Step 2: Which languages match, based on keywords alone?
        matchedLanguages = [language for language, languageData in self.languageKeywords.items() if self.basicLanguageHeuristic(language, languageData, dataset)]

        if not matchedLanguages:
            return self.result(False)

        # Step 3: Which languages match, based on a smarter lexer?
        lexer = ProgrammingLexer(matchedLanguages, data)
        matchedLanguages = lexer.lex()

        if not matchedLanguages:
            return self.result(False)


        # Basically giving ourselves a maximum of 50% confidence
        # This is temporary until we can work on the bayes classifier
        normalizer = 50 / float(max([scr for lexid, scr in matchedLanguages.items()]))
        normalScores = {}

        for langId, score in matchedLanguages.items():
            normalScores[langId] = int(round(normalizer * score))

        return self.resultMulti(normalScores)

        '''
        TODO:
        # Step 4: Which languages match, based on naive Bayes classification?
        bestResult = None
        for language in matchedLanguages:
            languageResult = self.bayesClassification(language, data)

            if not bestResult:
                bestResult = languageResult
            elif languageResult['confidence'] > bestResult['confidence']:
                bestResult = languageResult
        

        if not bestResult:
        return self.result(False)

        return self.result(True, bestResult['language'], bestResult['confidence'])
        '''

    def resultMulti(self, resultData):

        return ParseResultMulti([ParseResult(True, self.Type, self.languageKeywords[langId]['name'], confidence) for langId, confidence in resultData.items()])
