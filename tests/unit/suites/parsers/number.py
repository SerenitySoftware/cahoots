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

    def test_is_float(self):
        self.assertEqual((True, 123.123), self.np.is_float("123.123"))
        self.assertEqual((False, 0), self.np.is_float("abc"))

    def test_is_integer(self):
        self.assertEqual((True, 123), self.np.is_integer("123"))
        self.assertEqual((False, 0), self.np.is_integer("123.123"))
        self.assertEqual((False, 0), self.np.is_integer("abc"))

    def test_is_hex(self):
        self.assertEqual((True, 3735928559), self.np.is_hex("0xDEADBEEF"))
        self.assertEqual((True, 3735928559), self.np.is_hex("#0xDEADBEEF"))
        self.assertEqual((False, 0), self.np.is_hex("123.123"))

    def test_is_binary(self):
        self.assertEqual((True, "hello"), self.np.is_binary(
            "0110100001100101011011000110110001101111"
        ))
        self.assertEqual((False, 0), self.np.is_binary("1234"))
        self.assertEqual((False, 0), self.np.is_binary("1001"))
        self.assertEqual((False, 0), self.np.is_binary("10011"))
        self.assertEqual((False, 0), self.np.is_binary("100"))

    def test_is_octal(self):
        self.assertEqual((True, 2739128), self.np.is_octal("12345670"))
        self.assertEqual((False, 0), self.np.is_octal("1234567890"))

    def test_is_roman_numeral(self):
        self.assertEqual((True, 2646), self.np.is_roman_numeral("MMDCXLVI"))
        self.assertEqual((True, 4), self.np.is_roman_numeral("IV"))
        self.assertEqual((False, 0), self.np.is_roman_numeral("1234"))
        self.assertEqual(
            (False, 0),
            self.np.is_roman_numeral("I Am Sparticus!")
        )

    def test_is_fraction(self):
        self.assertEqual((True, "1 1/2"), self.np.is_fraction("1 1/2"))
        self.assertEqual((True, "34/68"), self.np.is_fraction("34/68"))
        self.assertEqual((False, 0), self.np.is_fraction("abc123"))
        self.assertEqual((False, 0), self.np.is_fraction("1 1/"))
        self.assertEqual((False, 0), self.np.is_fraction("1 1"))
        self.assertEqual((False, 0), self.np.is_fraction("1/2/4"))

    def test_isWordNumber(self):
        self.assertEqual((True, 1), self.np.is_words("One"))
        self.assertEqual((True, 200), self.np.is_words("Two Hundred"))
        self.assertEqual((True, 4533412), self.np.is_words(
            "Four Million Five Hundred and Thirty " +
            "Three Thousand Four Hundred and Twelve")
        )
        self.assertEqual((False, 0), self.np.is_words("foobar"))

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
            self.assertEqual(result.subtype, 'Fraction')
            self.assertEqual(result.result_value, '1/2')
            self.assertEqual(result.confidence, 94)
        self.assertEqual(count, 1)

    def mock_returnsFalse(self, param1):
        return False

    @mock.patch(
        'cahoots.parsers.equation.EquationParser.solve_equation',
        mock_returnsFalse
    )
    def test_parseWithNonSolveableFractionYieldsProperResult(self):
        count = 0
        for result in self.np.parse('1/2'):
            count += 1
            self.assertEqual(result.subtype, 'Fraction')
            self.assertEqual(result.result_value, '1/2')
            self.assertEqual(result.confidence, 54)
        self.assertEqual(count, 1)

    def test_parseWithBinaryYieldsProperResult(self):
        count = 0
        for result in self.np.parse(
                '0110100001100101011011000110110001101111'
        ):
            count += 1
            self.assertEqual(result.subtype, 'Binary')
            self.assertEqual(result.result_value, 'hello')
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWithIntegerNumberYieldsProperResult(self):
        count = 0
        for result in self.np.parse('123456789'):
            count += 1
            self.assertEqual(result.subtype, 'Integer')
            self.assertEqual(result.result_value, 123456789)
            self.assertEqual(result.confidence, 65)
        self.assertEqual(count, 1)

    def test_parseWithOctalNumberYieldsProperResult(self):
        count = 0
        for result in self.np.parse('2345'):
            count += 1
            if count == 1:
                self.assertEqual(result.subtype, 'Integer')
                self.assertEqual(result.result_value, 2345)
                self.assertEqual(result.confidence, 75)
            if count == 2:
                self.assertEqual(result.subtype, 'Octal')
                self.assertEqual(result.result_value, 1253)
                self.assertEqual(result.confidence, 25)
        self.assertEqual(count, 2)

    def test_parseWithFloatYieldsProperResult(self):
        count = 0
        for result in self.np.parse('35.75'):
            count += 1
            self.assertEqual(result.subtype, 'Decimal')
            self.assertEqual(result.result_value, 35.75)
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWithHexYieldsProperResult(self):
        count = 0
        for result in self.np.parse('0xDEADBEEF'):
            count += 1
            self.assertEqual(result.subtype, 'Hexadecimal')
            self.assertEqual(result.result_value, 3735928559)
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWithRomanNumeralYieldsProperResult(self):
        count = 0
        for result in self.np.parse('MMDCXLVI'):
            count += 1
            self.assertEqual(result.subtype, 'Roman Numeral')
            self.assertEqual(result.result_value, 2646)
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseWithWordsYieldsProperResult(self):
        count = 0
        for result in self.np.parse('Five Thousand'):
            count += 1
            self.assertEqual(result.subtype, 'Word Number')
            self.assertEqual(result.result_value, 5000)
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)
