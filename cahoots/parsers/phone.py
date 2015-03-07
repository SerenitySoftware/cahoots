from base import BaseParser
from uri import URIParser
from phonenumbers import phonenumberutil
from phonenumbers import geocoder
import string


class PhoneParser(BaseParser):

    punctuation = None
    letters = None
    digits = None

    def __init__(self, config):
        BaseParser.__init__(self, config, "Phone", 100)

    def getPhoneNumberObject(self, data_string):
        """Takes the data_string and tries to parse a phone number out of it"""

        try:
            checkRegion = (data_string[0] == "+")

            # First pass to see if it's a valid number
            numObj = phonenumberutil.parse(
                data_string,
                _check_region=checkRegion
            )

            numDesc = geocoder.description_for_valid_number(
                numObj, "en"
            ).strip()

        except:
            # If we can't parse it out, it's not a valid number
            return False

        """
        if we weren't able to check the region, and we didn't get a
        description we want to modify the data and give it another go
        with a country code added
        """
        if not checkRegion and not numDesc:
            prefix = None
            if len(self.digits) == 11 and data_string[0] == "1":
                prefix = "+"
            elif len(self.digits) == 10 \
                    and (data_string[0].isdigit() or
                         data_string[0] in string.punctuation):
                prefix = "+1"

            if prefix:
                try:
                    """
                    Second pass to see if we can get an actual
                    geocode out of it using a hammer
                    """
                    secondPass = phonenumberutil.parse(prefix + data_string)
                    numDesc = geocoder.description_for_valid_number(
                        secondPass, "en"
                    ).strip()
                    if numDesc:
                        numObj = secondPass
                        """
                        confidence hit because we had to
                        modify the data to get a result
                        """
                        self.confidence -= 5
                except:
                    pass

        # Attempting to get a valid region
        numRegion = phonenumberutil.region_code_for_number(numObj)

        """
        This is the compiled phone number data that
        we will use for the confidence decision
        """
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

    def parse(self, data_string, **kwargs):
        data_string = data_string.strip()

        self.digits = [c for c in data_string if c in string.digits]

        if len(data_string) > 30 or len(self.digits) < 7:
            return

        letter_set = set()
        self.letters = [c for c in data_string if
                        c in string.letters and
                        c not in letter_set and
                        not letter_set.add(c)]
        self.punctuation = [c for c in data_string if
                            c in string.punctuation or
                            c in string.whitespace]

        if len(self.letters) > len(self.digits):
            return

        # Parsing our input, looking for phone numbers
        phoneNumberData = self.getPhoneNumberObject(data_string)

        if not phoneNumberData:
            return

        # if this is an ip address, we take a big hit.
        if URIParser in self.Config.enabledModules:
            uriParser = URIParser(self.Config)
            if uriParser.is_ipv4_address(data_string):
                self.confidence -= 25

        # If this is an integer, we take a big hit.
        int_data_string = None
        try:
            int_data_string = int(data_string)
        except ValueError:
            pass

        if int_data_string is not None:
            self.confidence -= 20

        # Length penalties
        if len(self.digits) == 10:
            # Could be a 32bit integer
            self.confidence -= 5
        if len(self.digits) < 10:
            self.confidence -= 10

        # No description == not as strong
        if not phoneNumberData['description']:
            self.confidence -= 15

        # No region == not as strong
        if not phoneNumberData['region']:
            self.confidence -= 15

        """
        if there was punctuation, and we still see
        this as a phone number, we raise confidence
        """
        if len(self.punctuation) > 0:
            self.confidence += (5 * len(set(self.punctuation)))

        yield self.result(
            "Phone Number",
            max(0, min(100, self.confidence)),
            phoneNumberData
        )
