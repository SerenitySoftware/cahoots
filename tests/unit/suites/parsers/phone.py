from cahoots.parsers.phone import PhoneParser
from tests.unit.config import TestConfig
from phonenumbers import phonenumberutil
import unittest
import mock


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

    def descriptionForValidNumberMock(numObj, lang):
        PhoneParserTests.dfvnmCallCount += 1
        if PhoneParserTests.dfvnmCallCount == 1:
            return ""
        elif PhoneParserTests.dfvnmCallCount == 2:
            raise Exception("foo")

    def setUp(self):
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

        self.assertTrue(
            type(self.pp.get_phone_number_object("+1-979-549-5150")) is dict
        )

    def test_getphonenumberobjectWithTenDigitNoRegionAndNoDescTriesAgain(self):

        self.pp.digits = "1234567890"

        self.assertTrue(
            type(self.pp.get_phone_number_object("1234567890")) is dict
        )

    def test_getphonenumberobjectWith11DigitNoRegionAndNoDescTriesAgain(self):

        self.pp.digits = "11234567890"

        self.assertTrue(
            type(self.pp.get_phone_number_object("11234567890")) is dict
        )

    @mock.patch(
        "phonenumbers.geocoder.description_for_valid_number",
        descriptionForValidNumberMock
    )
    def test_getphonenumberobjectWhereSecondPassThrowsError(self):

        self.pp.digits = "1234567890"

        result = self.pp.get_phone_number_object("1234567890")

        self.assertEqual(2, PhoneParserTests.dfvnmCallCount)
        self.assertTrue(
            type(result) is dict
        )

    def test_parseWithInvalidLengthStringYieldsNothing(self):

        for result in self.pp.parse("1234"):
            self.assertFalse(result)

    def test_parseWithMoreLettersThanNumbersYieldsNothing(self):

        for result in self.pp.parse("abcdefghi1234567"):
            self.assertFalse(result)

    def test_parseWithInvalidPhoneYieldsNothing(self):

        for result in self.pp.parse("1234567123456712345671234567"):
            self.assertFalse(result)

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
