from cahoots.parsers.phone import PhoneParser
from tests.unit.config import TestConfig
from phonenumbers import phonenumberutil
import unittest

class PhoneParserTests(unittest.TestCase):
    """Unit Testing of the PhoneParser"""

    pp = None

    testDict = {
        "leadingZero": False,
        "extension": None,
        "countryCode": 1,
        "countryCodeSource": None,
        "carrierCode": None,
        "description": "Angleton, TX",
        "region": "US",
        "nationalNumber": 9795495150
    }

    def setUp(self):
        self.pp = PhoneParser(TestConfig())

    def tearDown(self):
        self.pp = None


    def test_buildPhoneNumberDict(self):

        numObj = phonenumberutil.parse("+1-979-549-5150")

        numDict = self.pp.buildPhoneNumberDict(numObj, "Angleton, TX", "US")

        self.assertEqual(numDict, self.testDict)


    def test_getPhoneNumberObject(self):

        self.assertFalse(self.pp.getPhoneNumberObject("The rain in spain falls mainly in the plain."))

        self.assertTrue(self.pp.getPhoneNumberObject("+1-979-549-5150"))