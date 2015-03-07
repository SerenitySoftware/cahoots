from cahoots.parsers.equation import EquationParser
from cahoots.parsers.programming import ProgrammingParser
from tests.unit.config import TestConfig
import unittest
import mock


class EquationParserTests(unittest.TestCase):
    """Unit Testing of the EquationParser"""

    ep = None

    def setUp(self):
        self.ep = EquationParser(TestConfig)

    def tearDown(self):
        self.ep = None

    def test_isSimpleEquation(self):

        self.assertTrue(self.ep.isSimpleEquation("5 * 5"))
        self.assertTrue(self.ep.isSimpleEquation("5(2**5"))
        self.assertTrue(self.ep.isSimpleEquation("5/4"))

        self.assertFalse(self.ep.isSimpleEquation("5 x 5"))
        self.assertFalse(self.ep.isSimpleEquation("3 DIVIDED BY 7"))
        self.assertFalse(self.ep.isSimpleEquation("3 TIMES 7"))

    def test_isTextEquation(self):

        self.assertTrue(self.ep.isTextEquation("3 TIMES 7"))
        self.assertTrue(self.ep.isTextEquation("3 DIVIDED BY 7"))
        self.assertTrue(self.ep.isTextEquation("3 DIVIDEDBY 7"))
        self.assertTrue(self.ep.isTextEquation("3 PLUS 7"))
        self.assertTrue(self.ep.isTextEquation("3 MINUS 7"))
        self.assertTrue(self.ep.isTextEquation("3 SQUARED"))
        self.assertTrue(self.ep.isTextEquation("3 CUBED"))
        self.assertTrue(self.ep.isTextEquation("SQUARE ROOT OF 3"))

        self.assertFalse(self.ep.isTextEquation("3 quadrided 7"))
        self.assertFalse(self.ep.isTextEquation("yo momma"))
        self.assertFalse(self.ep.isTextEquation("5 X 7"))

    def test_autoFloat(self):

        self.assertEqual(self.ep.autoFloat("123.123"), "float(123.123)")
        self.assertEqual(self.ep.autoFloat("123"), "float(123)")

    def test_autoMultiply(self):

        self.assertEqual(
            self.ep.autoMultiply("float(123.123)float(123.123)"),
            "float(123.123)*float(123.123)"
        )
        self.assertEqual(
            self.ep.autoMultiply("float(123.123)(float(47))"),
            "float(123.123)*(float(47))"
        )

    def test_checkForSafeEquationString(self):

        self.assertTrue(self.ep.checkForSafeEquationString(
            " math.sqrt float ( ) * + - / . 1 2 3 4 5 6 7 8 9 0 "
        ))

        self.assertFalse(self.ep.checkForSafeEquationString(
            " foo math.sqrt float ( ) * + - / . 1 2 3 4 5 6 7 8 9 0 "
        ))

    def test_solveEquation(self):

        self.assertEqual(self.ep.solveEquation("float(5) * float(5)"), 25.0)
        self.assertFalse(self.ep.solveEquation("asdf * float(5)"))
        self.assertFalse(self.ep.solveEquation("math.sqrt * float(5)"))

    def test_calculateConfidence(self):
        self.assertEqual(self.ep.calculateConfidence("979-549-5150"), 80)
        self.assertEqual(self.ep.calculateConfidence("1-979-549-5150"), 70)
        self.assertEqual(
            self.ep.calculateConfidence("the square root of 1234"),
            100
        )
        self.assertEqual(
            self.ep.calculateConfidence("Rain in spain is plain."),
            100
        )

    def mock_ProgrammingParserSet(self, data):
        return set([1, 2])

    @mock.patch(
        'cahoots.parsers.programming.ProgrammingParser.create_dataset',
        mock_ProgrammingParserSet
    )
    @mock.patch(
        'cahoots.parsers.programming.ProgrammingParser.find_common_tokens',
        mock_ProgrammingParserSet
    )
    def test_calculateConfidenceWithProgrammingParserLowersConfidence(self):
        TestConfig.enabledModules.append(ProgrammingParser)
        self.assertEqual(self.ep.calculateConfidence("979-549-5150"), 70)
        TestConfig.enabledModules.remove(ProgrammingParser)

    def test_parseSimpleNumberYieldsNothing(self):
        count = 0
        for result in self.ep.parse('1234'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseEssentiallyEmptyStringYieldsNothing(self):
        count = 0
        for result in self.ep.parse('THE'):
            count += 1
        self.assertEqual(count, 0)

    def test_parseSimpleEquationParseResult(self):
        count = 0
        for result in self.ep.parse('5 * 5'):
            count += 1
            self.assertEqual(result.Subtype, 'Simple')
            self.assertEqual(result.ResultValue, 25)
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseTextEquationParseResult(self):
        count = 0
        for result in self.ep.parse('3 TIMES 5'):
            count += 1
            self.assertEqual(result.Subtype, 'Text')
            self.assertEqual(result.ResultValue, 15)
            self.assertEqual(result.confidence, 100)
        self.assertEqual(count, 1)

    def test_parseNonParseableValueYieldsNothing(self):
        count = 0
        for result in self.ep.parse('This is not a text equation'):
            count += 1
        self.assertEqual(count, 0)
