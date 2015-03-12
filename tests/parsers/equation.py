# pylint: disable=duplicate-code
# pylint: disable=invalid-name,too-many-public-methods,missing-docstring

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
from cahoots.parsers.equation import EquationParser
from cahoots.parsers.programming import ProgrammingParser
from tests.parsers.location import SQLite3Mock
from cahoots.parsers.location.postalcode import PostalCodeParser
from tests.config import TestConfig
from SereneRegistry import registry
import unittest
import mock


class EquationParserTests(unittest.TestCase):
    """Unit Testing of the EquationParser"""

    ep = None

    def setUp(self):
        self.ep = EquationParser(TestConfig)

    def tearDown(self):
        SQLite3Mock.reset()
        registry.flush()
        self.ep = None

    def test_is_simple_equation(self):

        self.assertTrue(self.ep.is_simple_equation("5 * 5"))
        self.assertTrue(self.ep.is_simple_equation("5(2**5"))
        self.assertTrue(self.ep.is_simple_equation("5/4"))

        self.assertFalse(self.ep.is_simple_equation("5 x 5"))
        self.assertFalse(self.ep.is_simple_equation("3 DIVIDED BY 7"))
        self.assertFalse(self.ep.is_simple_equation("3 TIMES 7"))

    def test_is_text_equation(self):

        self.assertTrue(self.ep.is_text_equation("3 TIMES 7"))
        self.assertTrue(self.ep.is_text_equation("3 DIVIDED BY 7"))
        self.assertTrue(self.ep.is_text_equation("3 DIVIDEDBY 7"))
        self.assertTrue(self.ep.is_text_equation("3 PLUS 7"))
        self.assertTrue(self.ep.is_text_equation("3 MINUS 7"))
        self.assertTrue(self.ep.is_text_equation("3 SQUARED"))
        self.assertTrue(self.ep.is_text_equation("3 CUBED"))
        self.assertTrue(self.ep.is_text_equation("SQUARE ROOT OF 3"))

        self.assertFalse(self.ep.is_text_equation("3 quadrided 7"))
        self.assertFalse(self.ep.is_text_equation("yo momma"))
        self.assertFalse(self.ep.is_text_equation("5 X 7"))

    def test_auto_float(self):

        self.assertEqual(self.ep.auto_float("123.123"), "float(123.123)")
        self.assertEqual(self.ep.auto_float("123"), "float(123)")

    def test_auto_multiply(self):

        self.assertEqual(
            self.ep.auto_multiply("float(123.123)float(123.123)"),
            "float(123.123)*float(123.123)"
        )
        self.assertEqual(
            self.ep.auto_multiply("float(123.123)(float(47))"),
            "float(123.123)*(float(47))"
        )

    def test_check_for_safe_equation_string(self):

        self.assertTrue(self.ep.check_for_safe_equation_string(
            " math.sqrt float ( ) * + - / . 1 2 3 4 5 6 7 8 9 0 "
        ))

        self.assertFalse(self.ep.check_for_safe_equation_string(
            " foo math.sqrt float ( ) * + - / . 1 2 3 4 5 6 7 8 9 0 "
        ))

    def test_solve_equation(self):

        self.assertEqual(self.ep.solve_equation("float(5) * float(5)"), 25.0)
        self.assertFalse(self.ep.solve_equation("asdf * float(5)"))
        self.assertFalse(self.ep.solve_equation("math.sqrt * float(5)"))

    def test_calculate_confidence(self):
        self.assertEqual(self.ep.calculate_confidence("979-549-5150"), 80)
        self.assertEqual(self.ep.calculate_confidence("1-979-549-5150"), 70)
        self.assertEqual(
            self.ep.calculate_confidence("the square root of 1234"),
            100
        )
        self.assertEqual(
            self.ep.calculate_confidence("Rain in spain is plain."),
            100
        )

    @classmethod
    # pylint: disable=unused-argument
    def mock_ProgrammingParserSet(cls, data):
        return set([1, 2])

    @mock.patch(
        'cahoots.parsers.programming.ProgrammingParser.create_dataset',
        mock_ProgrammingParserSet
    )
    @mock.patch(
        'cahoots.parsers.programming.ProgrammingParser.find_common_tokens',
        mock_ProgrammingParserSet
    )
    def test_calculate_confidenceWithProgrammingParserLowersConfidence(self):
        TestConfig.enabledModules.append(ProgrammingParser)
        self.assertEqual(self.ep.calculate_confidence("979-549-5150"), 70)
        TestConfig.enabledModules.remove(ProgrammingParser)

    def test_parseSimpleNumberYieldsNothing(self):
        count = 0
        for _ in self.ep.parse('1234'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseEssentiallyEmptyStringYieldsNothing(self):
        count = 0
        for _ in self.ep.parse('THE'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseSimpleEquationParseResult(self):
        count = 0
        for result in self.ep.parse('5 * 5'):
            count += 1
            self.assertEqual(result.subtype, 'Simple')
            self.assertEqual(result.result_value, 25)
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseTextEquationParseResult(self):
        count = 0
        for result in self.ep.parse('3 TIMES 5'):
            count += 1
            self.assertEqual(result.subtype, 'Text')
            self.assertEqual(result.result_value, 15)
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseNonParseableValueYieldsNothing(self):
        count = 0
        for _ in self.ep.parse('This is not a text equation'):
            count += 1
        self.assertEqual(count, 0)

    @mock.patch('sqlite3.connect', SQLite3Mock.connect)
    def test_parse_postal_code_yields_result_with_lower_confidence(self):
        PostalCodeParser.bootstrap(TestConfig())
        SQLite3Mock.fetchall_returns = [
            [('us', 'united states')],
            [],
            [
                ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l')
            ]
        ]
        count = 0
        for result in self.ep.parse('90210-1210'):
            count += 1
            self.assertEqual(result.result_value, 89000)
            self.assertEqual(result.confidence, 75)
        self.assertEqual(1, count)
        self.assertEqual(
            SQLite3Mock.execute_calls,
            [
                (
                    'PRAGMA temp_store = 2',
                    None
                ),
                (
                    'SELECT * FROM city WHERE postal_code = ?',
                    ('90210-1210',)
                ),
                (
                    'SELECT * FROM city WHERE postal_code = ?',
                    ('90210',)
                ),
                (
                    'SELECT * FROM country WHERE abbreviation = ?',
                    ('a',)
                )
            ]
        )
