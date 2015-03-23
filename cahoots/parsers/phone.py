"""
The MIT License (MIT)

Copyright (c) Serenity Software, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from phonenumbers.phonenumberutil import NumberParseException
from phonenumbers import phonenumberutil
from phonenumbers import geocoder
from cahoots.parsers.base import BaseParser
from cahoots.parsers.uri import URIParser
import string


class PhoneParser(BaseParser):
    """Determines if given data is a phone number"""

    punctuation = None
    letters = None
    digits = None

    def __init__(self, config):
        BaseParser.__init__(self, config, "Phone", 100)

    def get_phone_number_object(self, data_string):
        """Takes the data_string and tries to parse a phone number out of it"""

        try:
            check_region = (data_string[0] == "+")

            # First pass to see if it's a valid number
            num_obj = phonenumberutil.parse(
                data_string,
                _check_region=check_region
            )

            num_desc = geocoder.description_for_valid_number(
                num_obj, "en"
            ).strip()

        except NumberParseException:
            # If we can't parse it out, it's not a valid number
            return False

        # if we weren't able to check the region, and we didn't get a
        # description we want to modify the data and give it another go
        # with a country code added
        if not check_region and not num_desc:
            prefix = None
            if len(self.digits) == 11 and data_string[0] == "1":
                prefix = "+"
            elif len(self.digits) == 10 \
                    and (data_string[0].isdigit() or
                         data_string[0] in string.punctuation):
                prefix = "+1"

            if prefix:
                try:
                    # Second pass to see if we can get an actual
                    # geocode out of it using a hammer
                    second_pass = phonenumberutil.parse(prefix + data_string)
                    num_desc = geocoder.description_for_valid_number(
                        second_pass, "en"
                    ).strip()
                    if num_desc:
                        num_obj = second_pass
                        # confidence hit because we had to
                        # modify the data to get a result
                        self.confidence -= 5
                except (NumberParseException, Exception):
                    pass

        # Attempting to get a valid region
        num_region = phonenumberutil.region_code_for_number(num_obj)

        # This is the compiled phone number data that
        # we will use for the confidence decision
        return self.build_phone_number_dict(num_obj, num_desc, num_region)

    @classmethod
    def build_phone_number_dict(cls, num_obj, num_desc, num_region):
        """Erase the contents of the object"""
        return {
            'countryCode': num_obj.country_code,
            'countryCodeSource': num_obj.country_code_source,
            'nationalNumber': num_obj.national_number,
            'extension': num_obj.extension,
            'leadingZero': num_obj.italian_leading_zero,
            'carrierCode': num_obj.preferred_domestic_carrier_code,
            'description': num_desc or None,
            'region': num_region or None,
        }

    def calculate_confidence(self, data_string, phone_number_data):
        """
        Various confidence calculations
        :param data_string: the data passed to the parser
        :type data_string: string
        :param phone_number_data: data that the phone number parsing produced
        :type phone_number_data: dict
        """
        # if this is an ip address, we take a big hit.
        if URIParser.is_ipv4_address(data_string):
            self.confidence -= 25

        # If this is an integer, we take a big hit.
        try:
            if int(data_string) is not None:
                self.confidence -= 20
        except ValueError:
            pass

        # Length penalties
        if len(self.digits) == 10:
            # Could be a 32bit integer
            self.confidence -= 5
        if len(self.digits) < 10:
            self.confidence -= 10

        # No description == not as strong
        if not phone_number_data['description']:
            self.confidence -= 15

        # No region == not as strong
        if not phone_number_data['region']:
            self.confidence -= 15

        # if there was punctuation, and we still see
        # this as a phone number, we raise confidence
        if len(self.punctuation) > 0:
            self.confidence += (5 * len(set(self.punctuation)))

    def parse(self, data_string):
        data_string = data_string.strip()

        # 30 is a stretch...
        if len(data_string) > 30:
            return

        self.digits = [c for c in data_string if c in string.digits]

        # We're just assuming less than 7 nums = not phone
        if len(self.digits) < 7:
            return

        letter_set = set()
        self.letters = [c for c in data_string if
                        c in string.letters and
                        c not in letter_set and
                        not letter_set.add(c)]

        # We don't believe this is a phone number if more letters than nums
        if len(self.letters) > len(self.digits):
            return

        self.punctuation = [c for c in data_string if
                            c in string.punctuation or
                            c in string.whitespace]

        # Parsing our input, looking for phone numbers
        phone_number_data = self.get_phone_number_object(data_string)

        if not phone_number_data:
            return

        self.calculate_confidence(data_string, phone_number_data)

        yield self.result(
            "Phone Number",
            max(0, min(100, self.confidence)),
            phone_number_data
        )
