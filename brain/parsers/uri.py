from base import BaseParser
import socket, urlparse
import string
from lepl.apps.rfc3696 import HttpUrl

class URIParser(BaseParser):

	def __init__(self):
		self.Type = "URI"
		self.Confidence = 50

	def isIPv6Address(self, address):
		try:
			socket.inet_pton(socket.AF_INET6, address)
			return True
		except:
			pass

		return False

	def isIPv4Address(self, address):
		try:
			socket.inet_aton(address)
			return True
		except:
			pass
			
		return False
		
	def tryURL(self, url):
		#using the lepl parsing library, which is slow
		#if HttpUrl()(url):
		#	return True
		
		pieces = urlparse.urlparse(url)
		
		if not all([pieces.scheme, pieces.netloc]):
			return False
			
		if not set(pieces.netloc) <= set(string.letters + string.digits + '-.') :
			return False
			
		return True
		
		
	def isURL(self, url):
		result = self.tryURL(url)
		
		if result:
			return True
			
		if '://' not in url:
			url = 'http://' + url
			result = self.tryURL(url)
			
			if result:
				return True
				
		return False
			

	def parse(self, dataString, **kwargs):
		if len(dataString) < 4:
			return
			
		dotCount = dataString.count(".")
		colonCount = dataString.count(":")
		
		if dotCount >= 2 or colonCount >= 2:
			if self.isIPv4Address(dataString):
				yield self.result("IP Address (v4)")
			
			if self.isIPv6Address(dataString):
				yield self.result("IP Address (v6)")
			
		letters = [c for c in dataString if c in string.letters]
		if dotCount > 0 and len(letters) >= 4 and self.isURL(dataString):
			yield self.result("URL")
		