from base import BaseParser

class ProgrammingParser(BaseParser):
	
	__subType = ''
	__success = False
	
	
	def __init__(self):
		self.Type = "Programming"
		self.Confidence = 20
	
	
	# Opening and closing tags
	def __findCommonTags(self, data):
		# Lots of languages use these types of opening tags
		if data.find('<?') != -1 or data.find('<%') != -1:
			self.Confidence += 10
			self.__success = True
			
			# Finding closing tags raises our 
			if data.find('?>') != -1 or data.find('%>') != -1:
				self.Confidence += 5
				
			# pretty good chance this is PHP...
			if (data.find('<?php') != -1):
				self.Confidence += 15
				self.__subType = 'PHP'
	
	
	# finding common words/phrases in programming languages
	def __findCommonTokens(self, data):
		
		tokens = [
			'#include','import','class','def','function','var','foreach','implements','extends',
			'private','public','protected','->',');','):','";',"';",'break','case'
		]
		
		# if we find any of the tokens we raise it by ten...only once
		for token in tokens:
			if data.find(token) != -1:
				self.Confidence += 10
				self.__success = True
				break
		
		
	def parse(self, data, **kwargs):
		
		self.__findCommonTags(data)
		
		self.__findCommonTokens(data)
		
		if self.__success == True:
			if self.Confidence > 100:
				self.Confidence = 100
				
			return self.result(True, self.__subType)
		else:
			return self.result(False)