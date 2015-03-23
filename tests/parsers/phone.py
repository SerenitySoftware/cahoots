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
# pylint: disable=invalid-name,too-many-public-methods,missing-docstring
from cahoots.parsers.phone import PhoneParser
from tests.config import TestConfig
from phonenumbers import phonenumberutil
import unittest
import mock


# pylint: disable=unused-argument
def descriptionForValidNumberMock(numObj, lang):
    PhoneParserTests.dfvnmCallCount += 1
    if PhoneParserTests.dfvnmCallCount == 1:
        return ""
    elif PhoneParserTests.dfvnmCallCount == 2:
        raise Exception("foo")


class PhoneParserTests(unittest.TestCase):
    """Unit Testing of the PhoneParser"""

    pp = None

    testDict = {
        "leadingZero": None,
        "extension": None,
        "countryCode": 1,
        "countryCodeSource": None,
        "carrierCode": None,
        "description": "Angleton, TX",
        "region": "US",
        "nationalNumber": 9795495150
    }

    dfvnmCallCount = 0

    def setUp(self):
        PhoneParser.bootstrap(TestConfig())
        self.pp = PhoneParser(TestConfig())

    def tearDown(self):
        self.pp = None
        PhoneParserTests.dfvnmCallCount = 0

    def test_build_phone_number_dict(self):

        numObj = phonenumberutil.parse("+1-979-549-5150")

        numDict = self.pp.build_phone_number_dict(numObj, "Angleton, TX", "US")

        self.assertEqual(numDict, self.testDict)

    def test_getphonenumberobjectWithNonNumberReturnsFalse(self):

        self.assertFalse(
            self.pp.get_phone_number_object(
                "The rain in spain falls mainly in the plain."
            )
        )

    def test_getphonenumberobjectWithRegionFlaggedPhoneReturnsDict(self):

        self.assertIsInstance(
            self.pp.get_phone_number_object("+1-979-549-5150"),
            dict
        )

    def test_getphonenumberobjectWithTenDigitNoRegionAndNoDescTriesAgain(self):

        self.pp.digits = "1234567890"

        self.assertIsInstance(
            self.pp.get_phone_number_object("1234567890"),
            dict
        )

    def test_getphonenumberobjectWith11DigitNoRegionAndNoDescTriesAgain(self):

        self.pp.digits = "11234567890"

        self.assertIsInstance(
            self.pp.get_phone_number_object("11234567890"),
            dict
        )

    @mock.patch(
        "phonenumbers.geocoder.description_for_valid_number",
        descriptionForValidNumberMock
    )
    def test_getphonenumberobjectWhereSecondPassThrowsError(self):

        self.pp.digits = "1234567890"

        result = self.pp.get_phone_number_object("1234567890")

        self.assertEqual(2, PhoneParserTests.dfvnmCallCount)
        self.assertIsInstance(result, dict)

    def test_parseWithInvalidLengthStringYieldsNothing(self):

        count = 1
        for _ in self.pp.parse("1234"):
            count -= 1
        self.assertEqual(1, count)

    def test_parseWithMoreLettersThanNumbersYieldsNothing(self):

        count = 1
        for _ in self.pp.parse("abcdefghi1234567"):
            count -= 1
        self.assertEqual(1, count)

    def test_parseWithInvalidPhoneYieldsNothing(self):

        count = 1
        for _ in self.pp.parse("1234567123456712345671234567"):
            count -= 1
        self.assertEqual(1, count)

    def test_parseWithIntegerYieldsExpectedConfidence(self):

        results = []
        for result in self.pp.parse("123123123123"):
            results.append(result)
            self.assertEqual(50, result.confidence)
        self.assertEqual(1, len(results))

    def test_parseWithIPAddressYieldsExpectedConfidence(self):

        results = []
        for result in self.pp.parse("123.123.123.123"):
            results.append(result)
            self.assertEqual(50, result.confidence)
        self.assertEqual(1, len(results))

    def test_parseWithTenDigitsYieldsExpectedConfidence(self):

        results = []
        for result in self.pp.parse("1231231231"):
            results.append(result)
            self.assertEqual(30, result.confidence)
        self.assertEqual(1, len(results))

    def test_parseWithNineDigitsYieldsExpectedConfidence(self):

        results = []
        for result in self.pp.parse("123123123"):
            results.append(result)
            self.assertEqual(15, result.confidence)
        self.assertEqual(1, len(results))

    def test_parseWithTooLongDataYieldsNothing(self):

        count = 5
        for _ in self.pp.parse("1231231234123123123412312312345"):
            count -= 1
        self.assertEqual(5, count)
