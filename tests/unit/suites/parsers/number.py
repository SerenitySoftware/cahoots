from cahoots.parsers.number import NumberParser
from tests.unit.config import TestConfig
import mock
import unittest


class NumberParserTests(unittest.TestCase):
    """Unit Testing of the NumberParser"""

    np = None

    def setUp(self):
        self.np = NumberParser(TestConfig)

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
        self.assertEqual((True, 3735928559), self.np.isHex("#0xDEADBEEF"))
        self.assertEqual((False, 0), self.np.isHex("123.123"))

    def test_isBinary(self):
        self.assertEqual((True, "hello"), self.np.isBinary(
            "0110100001100101011011000110110001101111"
        ))
        self.assertEqual((False, 0), self.np.isBinary("1234"))
        self.assertEqual((False, 0), self.np.isBinary("1001"))
        self.assertEqual((False, 0), self.np.isBinary("10011"))
        self.assertEqual((False, 0), self.np.isBinary("100"))

    def test_isOctal(self):
        self.assertEqual((True, 2739128), self.np.isOctal("12345670"))
        self.assertEqual((False, 0), self.np.isOctal("1234567890"))

    def test_isRomanNumeral(self):
        self.assertEqual((True, 2646), self.np.isRomanNumeral("MMDCXLVI"))
        self.assertEqual((True, 4), self.np.isRomanNumeral("IV"))
        self.assertEqual((False, 0), self.np.isRomanNumeral("1234"))
        self.assertEqual((False, 0), self.np.isRomanNumeral("I Am Sparticus!"))

    def test_isFraction(self):
        self.assertEqual((True, "1 1/2"), self.np.isFraction("1 1/2"))
        self.assertEqual((True, "34/68"), self.np.isFraction("34/68"))
        self.assertEqual((False, 0), self.np.isFraction("abc123"))
        self.assertEqual((False, 0), self.np.isFraction("1 1/"))
        self.assertEqual((False, 0), self.np.isFraction("1 1"))
        self.assertEqual((False, 0), self.np.isFraction("1/2/4"))

    def test_isWordNumber(self):
        self.assertEqual((True, 1), self.np.isWords("One"))
        self.assertEqual((True, 200), self.np.isWords("Two Hundred"))
        self.assertEqual((True, 4533412), self.np.isWords(
            "Four Million Five Hundred and Thirty " +
            "Three Thousand Four Hundred and Twelve")
        )
        self.assertEqual((False, 0), self.np.isWords("foobar"))

    def test_parseWithEmptyDataReturnsNone(self):
        count = 0
        for result in self.np.parse(''):
            count += 1
        self.assertEqual(count, 0)

    def test_parseWithStrippedDataReturnsNone(self):
        count = 0
        for result in self.np.parse('-,'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseWithFractionYieldsProperResult(self):
        count = 0
        for result in self.np.parse('1/2'):
            count += 1
            self.assertEqual(result.Subtype, 'Fraction')
            self.assertEqual(result.ResultValue, '1/2')
            self.assertEqual(result.Confidence, 94)
        self.assertEqual(count, 1)

    def mock_returnsFalse(self, param1):
        return False

    @mock.patch(
        'cahoots.parsers.equation.EquationParser.solveEquation',
        mock_returnsFalse
    )
    def test_parseWithNonSolveableFractionYieldsProperResult(self):
        count = 0
        for result in self.np.parse('1/2'):
            count += 1
            self.assertEqual(result.Subtype, 'Fraction')
            self.assertEqual(result.ResultValue, '1/2')
            self.assertEqual(result.Confidence, 54)
        self.assertEqual(count, 1)

    def test_parseWithBinaryYieldsProperResult(self):
        count = 0
        for result in self.np.parse(
                '0110100001100101011011000110110001101111'
        ):
            count += 1
            self.assertEqual(result.Subtype, 'Binary')
            self.assertEqual(result.ResultValue, 'hello')
            self.assertEqual(result.Confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWithIntegerNumberYieldsProperResult(self):
        count = 0
        for result in self.np.parse('123456789'):
            count += 1
            self.assertEqual(result.Subtype, 'Integer')
            self.assertEqual(result.ResultValue, 123456789)
            self.assertEqual(result.Confidence, 65)
        self.assertEqual(count, 1)

    def test_parseWithOctalNumberYieldsProperResult(self):
        count = 0
        for result in self.np.parse('145634524563452453453456'):
            count += 1
            if count == 1:
                self.assertEqual(result.Subtype, 'Integer')
                self.assertEqual(result.ResultValue, 145634524563452453453456)
                self.assertEqual(result.Confidence, 75)
            if count == 2:
                self.assertEqual(result.Subtype, 'Octal')
                self.assertEqual(result.ResultValue, 938994496129750423342)
                self.assertEqual(result.Confidence, 25)
        self.assertEqual(count, 2)

    def test_parseWithFloatYieldsProperResult(self):
        count = 0
        for result in self.np.parse('35.75'):
            count += 1
            self.assertEqual(result.Subtype, 'Decimal')
            self.assertEqual(result.ResultValue, 35.75)
            self.assertEqual(result.Confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWithHexYieldsProperResult(self):
        count = 0
        for result in self.np.parse('0xDEADBEEF'):
            count += 1
            self.assertEqual(result.Subtype, 'Hexadecimal')
            self.assertEqual(result.ResultValue, 3735928559)
            self.assertEqual(result.Confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWithRomanNumeralYieldsProperResult(self):
        count = 0
        for result in self.np.parse('MMDCXLVI'):
            count += 1
            self.assertEqual(result.Subtype, 'Roman Numeral')
            self.assertEqual(result.ResultValue, 2646)
            self.assertEqual(result.Confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWithWordsYieldsProperResult(self):
        count = 0
        for result in self.np.parse('Five Thousand'):
            count += 1
            self.assertEqual(result.Subtype, 'Word Number')
            self.assertEqual(result.ResultValue, 5000)
            self.assertEqual(result.Confidence, 100)
        self.assertEqual(count, 1)
