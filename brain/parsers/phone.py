from base import BaseParser
from uri import URIParser
from number import NumberParser
from phonenumbers import phonenumberutil, geocoder
import string, re

class PhoneParser(BaseParser):

    punctuation = None
    letters = None
    digits = None

    def __init__(self):
        self.Type = "Phone"
        self.Confidence = 100


    def getPhoneNumberObject(self, dataString):
        """Takes the datastring and tries to parse a phone number out of it"""

        try:
            checkRegion = (dataString[0] == "+")
            
            # First pass to see if it's a valid number
            numObj = phonenumberutil.parse(dataString, _check_region=checkRegion)

            numDesc = geocoder.description_for_valid_number(numObj, "en").strip()

        except:
            # If we can't parse it out, it's not a valid number
            return False


        # if we weren't able to check the region, and we didn't get a description
        # we want to modify the data and give it another go with a country code added
        if not checkRegion and not numDesc:
            prefix = None
            if len(self.digits) == 11 and dataString[0] == "1":
                prefix = "+"
            elif len(self.digits) == 10 and dataString[0] != "1" and (dataString[0].isdigit() or dataString[0] in string.punctuation):
                prefix = "+1"

            if prefix:
                try:
                    # Second pass to see if we can get an actual geocode out of it using a hammer
                    secondPass = phonenumberutil.parse(prefix + dataString)
                    numDesc = geocoder.description_for_valid_number(secondPass, "en").strip()
                    if numDesc:
                        numObj = secondPass
                        # confidence hit because we had to modify the data to get a result
                        self.Confidence -= 5
                except:
                    pass

        # Attempting to get a valid region
        numRegion = phonenumberutil.region_code_for_number(numObj)

        # This is the compiled phone number data that we will use for the confidence decision
        return self.buildPhoneNumberDict(numObj, numDesc, numRegion)


    def buildPhoneNumberDict(self, numObj, numDesc, numRegion):
        """Erase the contents of the object"""
        return {
            'countryCode': numObj.country_code,
            'countryCodeSource': numObj.country_code_source,
            'nationalNumber': numObj.national_number,
            'extension': numObj.extension,
            'leadingZero': numObj.italian_leading_zero,
            'carrierCode': numObj.preferred_domestic_carrier_code,
            'description': numDesc or None,
            'region': numRegion or None,
        }
            

    def parse(self, dataString, **kwargs):
        dataString = dataString.strip()
        
        if len(dataString) > 30 or len(dataString) < 7:
            return
            
        self.digits = [c for c in dataString if c in string.digits]
        letter_set = set()
        self.letters = [c for c in dataString if c in string.letters and c not in letter_set and not letter_set.add(c)]
        self.punctuation = [c for c in dataString if c in string.punctuation or c in string.whitespace]

        if len(self.letters) > len(self.digits):
            return
        
        # Parsing our input, looking for phone numbers
        phoneNumberData = self.getPhoneNumberObject(dataString)

        if not phoneNumberData:
            return

        # if this is an ip address, we take a big hit.
        uriParser = URIParser()
        if uriParser.isIPv4Address(dataString):
            self.Confidence -= 25

        # if this is an integer, we take a big hit.
        numParser = NumberParser()
        if numParser.isInteger(dataString):
            self.Confidence -= 20

        # Length penalties
        if len(self.digits) == 10:
            self.Confidence -= 5 # Could be a 32bit integer
        if len(self.digits) < 10:
            self.Confidence -= 10

        # No description == not as strong
        if not phoneNumberData['description']:
            self.Confidence -= 15

        # No region == not as strong
        if not phoneNumberData['region']:
            self.Confidence -= 15

        # if there was punctuation, and we still see this as a phone number, we raise confidence
        if len(self.punctuation) > 0:
            self.Confidence += (5 * len(set(self.punctuation)))
                                
        yield self.result("Phone Number", max(0, min(100, self.Confidence)), phoneNumberData)
