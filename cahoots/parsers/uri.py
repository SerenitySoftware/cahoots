from base import BaseParser
import socket
import urlparse
import string


class URIParser(BaseParser):

    def __init__(self, config):
        BaseParser.__init__(self, config, "URI", 100)

    def isIPv6Address(self, address):
        """Checks if the data is an ipv6 address"""
        try:
            socket.inet_pton(socket.AF_INET6, address)
            return True
        except:
            pass

        return False

    def isIPv4Address(self, address):
        """checks if the data is an ipv4 address"""
        try:
            socket.inet_aton(address)
            return True
        except:
            pass

        return False

    def isValidUrl(self, url):
        """Tries to parse a URL to see if it's valid"""
        pieces = urlparse.urlparse(url)

        if not all([pieces.scheme, pieces.netloc]):
            return False

        if not set(pieces.netloc) <=\
                set(string.letters + string.digits + '-.'):
            return False

        return True

    def parse(self, dataString, **kwargs):
        if len(dataString) < 4:
            return

        dotCount = dataString.count(".")
        colonCount = dataString.count(":")

        if dotCount >= 2 or colonCount >= 2:
            if self.isIPv4Address(dataString):
                """
                lowering the confidence because "Technically"
                and ipv4 address could be a phone number
                """
                self.Confidence -= 5
                yield self.result("IP Address (v4)")

            if self.isIPv6Address(dataString):
                yield self.result("IP Address (v6)")

        letters = [c for c in dataString if c in string.letters]

        if dotCount > 0 and len(letters) >= 4:
            if self.isValidUrl(dataString):
                yield self.result("URL")

            if '://' not in dataString:
                if self.isValidUrl('http://' + dataString):
                    # confidence hit since we had to modify the data
                    self.Confidence -= 25
                    yield self.result("URL", data='http://'+dataString)
