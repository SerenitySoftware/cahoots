from cahoots.parsers.number import NumberParser
import unittest

class NumberParserTests(unittest.TestCase):
    """Unit Testing of the NumberParser"""

    np = None

    def setUp(self):
        self.np = NumberParser()

    def tearDown(self):
        self.np = None


    def test_isFloat(self):

        self.assertEqual((True, 123.123), self.np.isFloat("123.123"))

        self.assertEqual((False, 0), self.np.isFloat("abc"))


    def test_isInteger(self):

        self.assertEqual((True, 123), self.np.isInteger("123"))

        self.assertEqual((False, 0), self.np.isInteger("123.123"))
        self.assertEqual((False, 0), self.np.isInteger("abc"))


    def test_isHex(self):

        self.assertEqual((True, 3735928559), self.np.isHex("0xDEADBEEF"))

        self.assertEqual((False, 0), self.np.isHex("123.123"))


    def test_isBinary(self):

        self.assertEqual((True, "hello"), self.np.isBinary("0110100001100101011011000110110001101111"))

        self.assertEqual((False, 0), self.np.isBinary("1234"))


    def test_isOctal(self):

        self.assertEqual((True, 2739128), self.np.isOctal("12345670"))

        self.assertEqual((False, 0), self.np.isOctal("1234567890"))


    def test_isRomanNumeral(self):

        self.assertEqual((True, 2646), self.np.isRomanNumeral("MMDCXLVI"))
        self.assertEqual((True, 4), self.np.isRomanNumeral("IV"))

        self.assertEqual((False, 0), self.np.isRomanNumeral("I Am Sparticus!"))


    def test_isFraction(self):

        self.assertEqual((True, "1 1/2"), self.np.isFraction("1 1/2"))
        self.assertEqual((True, "34/68"), self.np.isFraction("34/68"))

        self.assertEqual((False, 0), self.np.isFraction("abc123"))
        self.assertEqual((False, 0), self.np.isFraction("1 1/"))
        self.assertEqual((False, 0), self.np.isFraction("1 1"))

    def test_isWordNumber(self):
        self.assertEqual((True, 1), self.np.isWords("One"))
        self.assertEqual((True, 200), self.np.isWords("Two Hundred"))
        self.assertEqual((True, 4533412), self.np.isWords("Four Million Five Hundred and Thirty Three Thousand Four Hundred and Twelve"))