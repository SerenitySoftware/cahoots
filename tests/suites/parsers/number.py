from brain.parsers.number import NumberParser
import unittest

class NumberParserTests(unittest.TestCase):
    """Unit Testing of the NumberParser"""

    np = None

    def setUp(self):
        self.np = NumberParser()

    def tearDown(self):
        self.np = None


    def test_isFloat(self):

        self.assertTrue(self.np.isFloat("123.123"))

        self.assertFalse(self.np.isFloat("abc"))


    def test_isInteger(self):

        self.assertTrue(self.np.isInteger("123"))

        self.assertFalse(self.np.isInteger("123.123"))
        self.assertFalse(self.np.isInteger("abc"))


    def test_isHex(self):

        self.assertTrue(self.np.isHex("0xDEADBEEF"))

        self.assertFalse(self.np.isHex("123.123"))


    def test_isBinary(self):

        self.assertTrue(self.np.isBinary("0110100001100101011011000110110001101111"))

        self.assertFalse(self.np.isBinary("1234"))


    def test_decodeBinary(self):

        self.assertTrue(self.np.decodeBinary("0110100001100101011011000110110001101111"))

        self.assertFalse(self.np.decodeBinary("1234"))
        self.assertFalse(self.np.decodeBinary("0101010110101010"))


    def test_isOctal(self):

        self.assertTrue(self.np.isOctal("12345670"))

        self.assertFalse(self.np.isOctal("1234567890"))


    def test_isRomanNumeral(self):

        self.assertTrue(self.np.isRomanNumeral("MMDCXLVI"))
        self.assertTrue(self.np.isRomanNumeral("IV"))

        self.assertFalse(self.np.isRomanNumeral("I Am Sparticus!"))


    def test_isFraction(self):

        self.assertTrue(self.np.isFraction("1 1/2"))
        self.assertTrue(self.np.isFraction("34/68"))

        self.assertFalse(self.np.isFraction("abc123"))
        self.assertFalse(self.np.isFraction("1 1/"))
        self.assertFalse(self.np.isFraction("1 1"))