from brain import parser
from tests import getFixtureFileContents
import unittest


class BrainiacTest(unittest.TestCase):
    
    def perform(self, data, expected_type, expected_subtype):
        results = parser.parse(data)['results']['matches']
        self.assertNotEqual(0, len(results), msg = "No Brainiac results returned")
        
        top_result = results[0]
        self.assertEqual(top_result.Type, expected_type, msg = "Top result was {0} instead of expected result {1}".format(top_result.Type, expected_type))
        self.assertEqual(top_result.Subtype, expected_subtype, msg = "Top result subtype was {0} instead of expected subtype {1}".format(top_result.Subtype, expected_subtype))


class NumberTests(BrainiacTest):

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
        self.perform("0001", "Number", "Binary")
        
    def test_roman_numerals(self):
        self.perform("XIV", "Number", "Roman Numeral")
        self.perform("XXX", "Number", "Roman Numeral")
        self.perform("LXXXIX", "Number", "Roman Numeral")
        self.perform("DCXCI", "Number", "Roman Numeral")
        self.perform("MMMMCCCIX", "Number", "Roman Numeral")
        
    def test_fractions(self):
        self.perform("1 1/2", "Number", "Fraction")


class CharacterTests(BrainiacTest):
    
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


class URITests(BrainiacTest):
    
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
        self.perform("http://www.activecollab.com/docs/manuals/admin/tweak/url-formats", "URI", "URL")
        self.perform("http://example.com/public/index.php?/projects/12", "URI", "URL")
        self.perform("http://example.com/public/index.php#anything", "URI", "URL")


class EmailTests(BrainiacTest):
    
    def test_email(self):
        self.perform("jambra@photoflit.com", "Email", "Email Address")
        self.perform("jambra+brainiac@photoflit.com", "Email", "Email Address")
        self.perform("jambra@smithsonian.museum", "Email", "Email Address")
        self.perform("jambra@photoflit.co.uk", "Email", "Email Address")


class PhoneTests(BrainiacTest):
    
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
        self.perform("030/2829352", "Phone", "Phone Number")
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


class DateTester(BrainiacTest):
    
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


class EquationTester(BrainiacTest):
    
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


class ProgrammingTester(BrainiacTest):

    def test_programming(self):
        self.perform(getFixtureFileContents('actionscript.as'), 'Programming', 'ActionScript')
        self.perform(getFixtureFileContents('c++.cpp'), 'Programming', 'C++')
        self.perform(getFixtureFileContents('c.c'), 'Programming', 'C')
        self.perform(getFixtureFileContents('csharp.cs'), 'Programming', 'C#')
        self.perform(getFixtureFileContents('java.java'), 'Programming', 'Java')
        self.perform(getFixtureFileContents('javascript.js'), 'Programming', 'JavaScript')
        self.perform(getFixtureFileContents('perl.pl'), 'Programming', 'Perl')
        self.perform(getFixtureFileContents('php.php'), 'Programming', 'PHP')
        self.perform(getFixtureFileContents('python.py'), 'Programming', 'Python')
        self.perform(getFixtureFileContents('ruby.rb'), 'Programming', 'Ruby')
        self.perform(getFixtureFileContents('visualbasic.vb'), 'Programming', 'Visual Basic')
