from cahoots.parsers.base import BaseParser
from cahoots.parsers.programming.lexer import ProgrammingLexer
from cahoots.parsers.programming.bayesian import ProgrammingBayesianClassifier
from cahoots.result import ParseResult
from cahoots.util import BrainRegistry
import os, re, glob, yaml


class ProgrammingParser(BaseParser):

    allKeywords = []
    languageKeywords = {}

    @staticmethod
    def bootstrap():
        """Loads tokens from the yaml files on disk"""
        allKeywords = []
        languageKeywords = {}

        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "languages/*.yaml")

        for filePath in glob.glob(path):
            with open(filePath, 'r') as languageFile:
                language = yaml.load(languageFile)
                allKeywords.extend(language['keywords'])
                languageKeywords[language['id']] = language

        BrainRegistry.set('PPallKeywords', set(allKeywords))
        BrainRegistry.set('PPlanguageKeywords', languageKeywords)

        ProgrammingBayesianClassifier.bootstrap();


    def __init__(self):
        self.Type = "Programming"
        self.Confidence = 0
        self.allKeywords = BrainRegistry.get('PPallKeywords')
        self.languageKeywords = BrainRegistry.get('PPlanguageKeywords')
    

    # finding common words/phrases in programming languages
    def findCommonTokens(self, dataset):
        return [keyword for keyword in dataset if keyword in self.allKeywords]


    def basicLanguageHeuristic(self, language, languageData, dataset):
        return [keyword for keyword in dataset if keyword in languageData['keywords']]


    def createDataset(self, data):
        """Takes a data string and converts it into a dataset for analysis"""
        return set(re.split('[ ;,{}()\n\t\r]', data.lower()))


    def parse(self, data, **kwargs):
        """Determines if the data is an example of one of our trained languages"""

        dataset = self.createDataset(data)


        # Step 1: Is this possibly code?
        if not self.findCommonTokens(dataset):
            return
        

        # Step 2: Which languages match, based on keywords alone?
        matchedLanguages = [language for language, languageData in self.languageKeywords.items() if self.basicLanguageHeuristic(language, languageData, dataset)]

        if not matchedLanguages:
            return


        # Step 3: Which languages match, based on a smarter lexer?
        lexer = ProgrammingLexer(matchedLanguages, data.lower())
        lexedLanguages = lexer.lex()

        if not lexedLanguages:
            return

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

        for langId, confidence in normalScores.items():
            yield ParseResult(self.Type, self.languageKeywords[langId]['name'], confidence)
