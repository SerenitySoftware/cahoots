from base import BaseParser
from number import NumberParser
import re

class NameParser(BaseParser):

    prefixes = ['MS','MISS','MRS','MR','MASTER','REV','FR','DR','ATTY','PROF','HON','PRES','GOV','COACH','OFC','MSGR','SR','BR','SUPT','REP','SEN','AMB','TREAS','SEC','PVT','CPL','SGT','ADM','MAJ','CAPT','CMDR','LT','COL','GEN']
    suffixes = ['AB','BA','BFA','BTECH','LLB','BSC','MA','MFA','LLM','MLA','MBA','MSC','JD','MD','DO','PHARMD','PHD','DPHIL','LLD','ENGD','KBE','LLD','DD','ESQ','ESQUIRE','CSA','ASCAP','CA','CPA','CFA','PE','PG','CPL','CENG','RA','AIA','RIBA','MEOA','CISA','CISSP','CISM','PT','DPT','MCSP','SRP','RGN','USN','USMC','OFM','CSV','JR','SR','JNR','SNR','2ND','3RD','4TH','5TH','6TH','7TH','8TH','9TH','BT','BART','QC','MP','SSF','FRCP','FRSA','RAF','RN','RMP','FAIA','FRSE','SJ','OP','ICMA-CM','MBASW']

    def __init__(self):
        self.Type = "Name"
        self.Confidence = 0


    def basicValidation(self, data):
        """Make sure every word in the phrase either starts with a Capital Letter or a Number"""
        return len(data) == len([word for word in data if (word[0].isupper() or (len(data)>1 and word[0].isdigit())) and not word.isdigit()])


    def isPrefix(self, word):
        """Checks to see if the word passed in is a name prefix"""
        word = word.replace('.', '').upper()
        return word in self.prefixes


    def isSuffix(self, word):
        """Checks to see if the word passed in is a name suffix"""
        np = NumberParser()
        if np.isRomanNumeral(word):
            return True

        word = word.replace('.', '').upper()
        return word in self.suffixes


    def isInitial(self, word):
        """Checks to see if the word passed in is an initial"""
        if len(word) > 2:
            return False

        if len(word) == 1:
            return word[0].isalpha()

        if len(word) == 2:
            return word[1] == '.' and word[0].isalpha()

    
    def parse(self, data, **kwargs):
        """Determines if the data is a name or not"""

        # Making sure there are at least SOME uppercase letters in the phrase
        if not re.search('[A-Z]', data):
            return self.result(False)

        data = data.split()


        # If someone has a name longer than 10 words...they need help
        # Making sure each word in the phrase starts with an uppercase letter or a number
        if len(data) > 10 or not self.basicValidation(data):
            return self.result(False)


        # Checking for things like Mr. or Jr. Big boost for these values.
        # If found, we remove them from the list of words
        if len(data) > 2:
            if self.isPrefix(data[0]):
                data.pop(0)
                self.Confidence += 20
            if self.isSuffix(data[-1]):
                data.pop()
                self.Confidence += 20


        # If all we found was a prefix and a suffix, basically zero confidence.
        if len(data) == 0:
            return self.result(False)


        # If we have a two or three word "name" here we boost its confidence since this is something of a giveaway
        if len(data) < 4 and len(data) > 1:
            self.Confidence += (5 * len(data))


        # Adding confidence for initials vs words, if we have greater than one word
        if len(data) > 1:
            for word in data:
                if self.isInitial(word):
                    self.Confidence += 20
                else:
                    self.Confidence += 15


        if self.Confidence == 0:
            return self.result(False)

        return self.result(True, "Name", min(100, self.Confidence))