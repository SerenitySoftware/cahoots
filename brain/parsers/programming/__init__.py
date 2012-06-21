from brain.parsers.base import BaseParser
import os
import re
import glob
import yaml

class ProgrammingParser(BaseParser):
	
	__subType = ''
	__success = False

	all_keywords = []
	language_keywords = {}
	
	
	def __init__(self):
		self.Type = "Programming"
		self.Confidence = 0

		self.loadTokens()
		

	def loadTokens(self):
		directory = os.path.dirname(os.path.abspath(__file__))
		path = os.path.join(directory, "languages/*.yaml")

		for file_path in glob.glob(path):
			with open(file_path, 'r') as language_file:
				language = yaml.load(language_file)
				self.all_keywords.extend(language['keywords'])
				self.language_keywords[language['name']] = language
	
	# finding common words/phrases in programming languages
	def findCommonTokens(self, data):
		dataset = re.split('[ ;,{}()\n\t]', data)

		#an empty list is considered False
		return [keyword for keyword in dataset if keyword in self.all_keywords]

	def basicLanguageHeuristic(self, language, data):
		return True

	def lexerMatcher(self, language, data):
		return True

	def bayesClassification(self, language, data):
		return { 'confidence': 100, 'language': language }
		
	def parse(self, data, **kwargs):
		
		print self.findCommonTokens(data)

		#Step 1: Is this even code?
		if not self.findCommonTokens(data):
			return self.result(False)

		'''
		#Step 2: Which languages match, based on keywords alone?
		matched_languages = [language for language, language_data in self.language_keywords.items() if self.basicLanguageHeuristic(language, language_data)]


		#Step 3: Which languages match, based on a smarter lexer?
		matched_languages = [language for language in matched_languages if self.lexerMatcher(language, data)]

		if not matched_languages:
			return self.result(False)


		#Step 4: Which languages match, based on naive Bayes classification?
		best_result = None
		for language in matched_languages:
			language_result = self.bayesClassification(language, data)

			if not best_result:
				best_result = language_result
			elif language_result['confidence'] > best_result['confidence']:
				best_result = language_result
		

		if not best_result:'''
		return self.result(False)

		return self.result(True, best_result['language'], best_result['confidence'])

