from base import BaseParser
import urlparse
import string
import win_inet_pton   # NOQA
import socket


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

    def parse(self, data_string, **kwargs):
        if len(data_string) < 4:
            return

        dotCount = data_string.count(".")
        colonCount = data_string.count(":")

        if dotCount >= 2 or colonCount >= 2:
            if self.isIPv4Address(data_string):
                """
                lowering the confidence because "Technically"
                and ipv4 address could be a phone number
                """
                self.Confidence -= 5
                yield self.result("IP Address (v4)")

            elif self.isIPv6Address(data_string):
                yield self.result("IP Address (v6)")

        letters = [c for c in data_string if c in string.letters]

        if dotCount > 0 and len(letters) >= 4:
            if self.isValidUrl(data_string):
                yield self.result("URL")

            elif '://' not in data_string:
                if self.isValidUrl('http://' + data_string):
                    # confidence hit since we had to modify the data
                    self.Confidence -= 25
                    yield self.result("URL", data='http://'+data_string)
