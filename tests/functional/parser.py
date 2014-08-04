#!/usr/bin/python

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__))[:-17])

from cahoots.parser import CahootsParser
from SereneRegistry import registry
from tests.unit.config import TestConfig
import unittest

"""
These are functional/acceptance tests of the parser.
We're using the unit test system since it's easy to
work with for this kind of testing.
"""


class CahootsTest(unittest.TestCase):

    parser = None

    def setUp(self):
        self.parser = CahootsParser(TestConfig())

    def tearDown(self):
        self.parser = None
        registry.flush()

    def perform(self, data, expected_type, expected_subtype):
        results = self.parser.parse(data)['results']['matches']
        self.assertNotEqual(
            0,
            len(results),
            msg="No Cahoots results returned"
        )

        top_result = self.parser.parse(data)['top']
        self.assertEqual(
            top_result.Type,
            expected_type,
            msg="Top result was {0} instead of expected result {1}"
            .format(top_result.Type, expected_type)
        )
        self.assertEqual(
            top_result.Subtype,
            expected_subtype,
            msg="Top result subtype was {0} instead of expected subtype {1}"
            .format(top_result.Subtype, expected_subtype)
        )


class BooleanTests(CahootsTest):
    """
    Not testing 1 or 0 here, because they have a
    higher confidence of being an integer
    """

    def test_true(self):
        self.perform("true", "Boolean", "True")
        self.perform("yes", "Boolean", "True")
        self.perform("yep", "Boolean", "True")
        self.perform("yup", "Boolean", "True")
        self.perform("t", "Boolean", "True")

    def test_false(self):
        self.perform("false", "Boolean", "False")
        self.perform("no", "Boolean", "False")
        self.perform("nope", "Boolean", "False")
        self.perform("f", "Boolean", "False")


class NumberTests(CahootsTest):

    def test_integers(self):
        self.perform("1", "Number", "Integer")
        self.perform("123", "Number", "Integer")
        self.perform("-50", "Number", "Integer")
        self.perform("1443", "Number", "Integer")
        self.perform("-4994", "Number", "Integer")
        self.perform("-100,440", "Number", "Integer")

    def test_decimals(self):
        self.perform("1.0", "Number", "Decimal")
        self.perform("10.0", "Number", "Decimal")
        self.perform("100,000.00", "Number", "Decimal")
        self.perform("94092420490294092409.0", "Number", "Decimal")
        self.perform("-0.0", "Number", "Decimal")
        self.perform("-100,000.00", "Number", "Decimal")

    def test_hexadecimals(self):
        self.perform("0xdeadbeef", "Number", "Hexadecimal")
        self.perform("0xDEADBEEF", "Number", "Hexadecimal")
        self.perform("#FFFFFF", "Number", "Hexadecimal")

    def test_binary(self):
        self.perform("0010100101011001", "Number", "Binary")
        self.perform("00110001001100100011001100110100", "Number", "Binary")

    def test_roman_numerals(self):
        self.perform("XIV", "Number", "Roman Numeral")
        self.perform("XXX", "Number", "Roman Numeral")
        self.perform("LXXXIX", "Number", "Roman Numeral")
        self.perform("DCXCI", "Number", "Roman Numeral")
        self.perform("MMMMCCCIX", "Number", "Roman Numeral")

    def test_fractions(self):
        self.perform("1 1/2", "Number", "Fraction")


class CharacterTests(CahootsTest):

    def test_letters(self):
        self.perform("a", "Character", "Letter")
        self.perform("A", "Character", "Letter")

    def test_punctuation(self):
        self.perform("?", "Character", "Punctuation")
        self.perform("-", "Character", "Punctuation")
        self.perform("/", "Character", "Punctuation")

    def test_whitespace(self):
        self.perform(" ", "Character", "Whitespace")
        self.perform("\t", "Character", "Whitespace")


class URITests(CahootsTest):

    def test_IPv4(self):
        self.perform("127.0.0.1", "URI", "IP Address (v4)")
        self.perform("0.0.0.0", "URI", "IP Address (v4)")
        self.perform("192.168.1.1", "URI", "IP Address (v4)")

    def test_IPv6(self):
        self.perform("2607:f0d0:1002:51::4", "URI", "IP Address (v6)")

    def test_urls(self):
        self.perform("www.google.com", "URI", "URL")
        self.perform("http://www.google.com", "URI", "URL")
        self.perform("google.com", "URI", "URL")
        self.perform(
            "http://www.activecollab.com/docs/manuals/admin/tweak/url-formats",
            "URI",
            "URL"
        )
        self.perform(
            "http://example.com/public/index.php?/projects/12",
            "URI",
            "URL"
        )
        self.perform(
            "http://example.com/public/index.php#anything",
            "URI",
            "URL"
        )


class EmailTests(CahootsTest):

    def test_email(self):
        self.perform("jambra@photoflit.com", "Email", "Email Address")
        self.perform("jambra+cahoots@photoflit.com", "Email", "Email Address")
        self.perform("jambra@smithsonian.museum", "Email", "Email Address")
        self.perform("jambra@photoflit.co.uk", "Email", "Email Address")


class PhoneTests(CahootsTest):

    def test_phone(self):
        self.perform("972-955-2538", "Phone", "Phone Number")
        self.perform("(02) 1234 5678", "Phone", "Phone Number")
        self.perform("0412 345 67", "Phone", "Phone Number")
        self.perform("04716 432", "Phone", "Phone Number")
        self.perform("(02)123 456", "Phone", "Phone Number")
        self.perform("(31) 1234-5678", "Phone", "Phone Number")
        self.perform("(514) 555-4000", "Phone", "Phone Number")
        self.perform("043 123 45 67", "Phone", "Phone Number")
        self.perform("2 123 4567", "Phone", "Phone Number")
        self.perform("(012)12345678", "Phone", "Phone Number")
        self.perform("(0123)12345678", "Phone", "Phone Number")
        self.perform("212 345 678", "Phone", "Phone Number")
        self.perform("3012 3456", "Phone", "Phone Number")
        self.perform("915 216 491", "Phone", "Phone Number")
        self.perform("09 1234 5678", "Phone", "Phone Number")
        self.perform("01 56 60 56 60", "Phone", "Phone Number")
        self.perform("020 1234 5678", "Phone", "Phone Number")
        self.perform("2345 6789", "Phone", "Phone Number")
        self.perform("080 2134 5678", "Phone", "Phone Number")
        self.perform("(03) 1234-5678", "Phone", "Phone Number")
        self.perform("020 3601234", "Phone", "Phone Number")
        self.perform("239 12 34", "Phone", "Phone Number")
        self.perform("(010) 2345678", "Phone", "Phone Number")
        self.perform("(0123) 456789", "Phone", "Phone Number")
        self.perform("(04) 234 5678", "Phone", "Phone Number")
        self.perform("021 345 678", "Phone", "Phone Number")
        self.perform("23 45 67 89", "Phone", "Phone Number")
        self.perform("22 123 45 67", "Phone", "Phone Number")
        self.perform("213 123 456", "Phone", "Phone Number")
        self.perform("(495) 123-45-67", "Phone", "Phone Number")
        self.perform("08-123 456 78", "Phone", "Phone Number")
        self.perform("0 2123 1234", "Phone", "Phone Number")
        self.perform("08 1234 1234", "Phone", "Phone Number")
        self.perform("(03) 123-5678", "Phone", "Phone Number")
        self.perform("(02) 8765-4321", "Phone", "Phone Number")
        self.perform("(650) 555-4000", "Phone", "Phone Number")
        self.perform("+44 (013) 33-44-122 ext 33549", "Phone", "Phone Number")


class DateTester(CahootsTest):

    def test_dates(self):
        self.perform("12/1/2004", "Date", "Date")
        self.perform("1997-04-13", "Date", "Date")
        self.perform("1997-07-16T19:20+01:00", "Date", "Date")
        self.perform("1997-07-16T19:20:30+01:00", "Date", "Date")
        self.perform("1997-07-16T19:20:30.45+01:00", "Date", "Date")
        self.perform("1994-11-05T08:15:30-05:00", "Date", "Date")
        self.perform("1994-11-05T13:15:30Z", "Date", "Date")
        self.perform("March 16, 1985", "Date", "Date")
        self.perform("March 16th, 1985", "Date", "Date")
        self.perform("Mar 16 1985", "Date", "Date")
        self.perform("16 Mar 1985", "Date", "Date")


class EquationTester(CahootsTest):

    def test_simple(self):
        self.perform("5 x 5", "Equation", "Simple")
        self.perform("(2*3)^4", "Equation", "Simple")
        self.perform("1/7+4-2", "Equation", "Simple")
        self.perform("124*76(45^4)-34.51+2345", "Equation", "Simple")

    def test_textual(self):
        self.perform("square root of 16", "Equation", "Text")
        self.perform("The square root of 169", "Equation", "Text")
        self.perform("square root of 123.456", "Equation", "Text")
        self.perform("The square root of 169 * 3", "Equation", "Text")
        self.perform("(square ROOT of 169) * 35", "Equation", "Text")
        self.perform("45 squared", "Equation", "Text")
        self.perform("45 cubed", "Equation", "Text")
        self.perform("45 minus 34", "Equation", "Text")
        self.perform("45 plus 34", "Equation", "Text")
        self.perform("45 times 34", "Equation", "Text")
        self.perform("45 divided by 34", "Equation", "Text")
        self.perform("45 dividedby 34", "Equation", "Text")


class NameTester(CahootsTest):

    def test_programming(self):
        self.perform('Mr Ryan W Vennell Sr', 'Name', 'Name')
        self.perform('Mr R Vennell Sr', 'Name', 'Name')
        self.perform('Ryan W. Vennell Sr', 'Name', 'Name')
        self.perform('Mr Ryan Vennell Esq', 'Name', 'Name')
        self.perform('Mr Ryan W Vennell', 'Name', 'Name')
        self.perform('Ryan Vennell', 'Name', 'Name')
        self.perform('R. Vennell', 'Name', 'Name')
        self.perform('R Vennell', 'Name', 'Name')
        self.perform('Ryan V', 'Name', 'Name')
        self.perform('Ryan V.', 'Name', 'Name')


class MeasurementTester(CahootsTest):

    def test_measurement(self):
        self.perform('73 Inches', 'Measurement', 'Imperial Length')
        self.perform('73"', 'Measurement', 'Imperial Length')
        self.perform('73\'', 'Measurement', 'Imperial Length')
        self.perform('5 acres', 'Measurement', 'Imperial Area')
        self.perform('5 sq/ft', 'Measurement', 'Imperial Area')
        self.perform('7 ounces', 'Measurement', 'Imperial Mass')
        self.perform('5lb', 'Measurement', 'Imperial Mass')
        self.perform('7 deg F', 'Measurement', 'Imperial Temperature')
        self.perform('10000 Gallons', 'Measurement', 'Imperial Volume')
        self.perform('1 pint of icecream', 'Measurement', 'Imperial Volume')
        self.perform('15 hectares', 'Measurement', 'Metric Area')
        self.perform('15 square kilometers', 'Measurement', 'Metric Area')
        self.perform('10nm', 'Measurement', 'Metric Length')
        self.perform('43 kilometers', 'Measurement', 'Metric Length')
        self.perform('70 metric tonnes', 'Measurement', 'Metric Mass')
        self.perform('3kg', 'Measurement', 'Metric Mass')
        self.perform('7 celcius', 'Measurement', 'Metric Temperature')
        self.perform('3 liter', 'Measurement', 'Metric Volume')
        self.perform('3 ml', 'Measurement', 'Metric Volume')
        self.perform('400 parsecs', 'Measurement', 'Miscellaneous Length')


if __name__ == '__main__':
    unittest.main()
