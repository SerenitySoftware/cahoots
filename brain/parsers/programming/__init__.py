from brain.parsers.base import BaseParser
import os
import re
import glob
import yaml

class ProgrammingParser(BaseParser):
	
	__subType = ''
	__success = False

	allKeywords = []
	languageKeywords = {}
	
	
	def __init__(self):
		self.Type = "Programming"
		self.Confidence = 0

		self.loadTokens()
		

	def loadTokens(self):
		directory = os.path.dirname(os.path.abspath(__file__))
		path = os.path.join(directory, "languages/*.yaml")

		for filePath in glob.glob(path):
			with open(filePath, 'r') as languageFile:
				language = yaml.load(languageFile)
				self.allKeywords.extend(language['keywords'])
				self.languageKeywords[language['name']] = language

		self.allKeywords = set(self.allKeywords)
	
	# finding common words/phrases in programming languages
	def findCommonTokens(self, dataset):
		return [keyword for keyword in dataset if keyword in self.allKeywords]

	def basicLanguageHeuristic(self, language, languageData, dataset):
		return [keyword for keyword in dataset if keyword in languageData['keywords']]

	def lexerMatcher(self, language, data):
		return True

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
		if self.findCommonTokens(dataset):
			return self.result(False)
		
		#Step 2: Which languages match, based on keywords alone?
		matchedLanguages = [language for language, languageData in self.languageKeywords.items() if self.basicLanguageHeuristic(language, languageData, dataset)]


		'''
		#Step 3: Which languages match, based on a smarter lexer?
		matchedLanguages = [language for language in matchedLanguages if self.lexerMatcher(language, data)]

		if not matchedLanguages:
			return self.result(False)


		#Step 4: Which languages match, based on naive Bayes classification?
		bestResult = None
		for language in matchedLanguages:
			languageResult = self.bayesClassification(language, data)

			if not bestResult:
				bestResult = languageResult
			elif languageResult['confidence'] > bestResult['confidence']:
				bestResult = languageResult
		

		if not bestResult:'''
		return self.result(False)

		return self.result(True, bestResult['language'], bestResult['confidence'])

