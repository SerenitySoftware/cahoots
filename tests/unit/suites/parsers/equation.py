from cahoots.parsers.equation import EquationParser
from tests.unit.config import TestConfig
import unittest

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

        self.assertEqual(self.ep.autoMultiply("float(123.123)float(123.123)"), "float(123.123)*float(123.123)")
        self.assertEqual(self.ep.autoMultiply("float(123.123)(float(47))"), "float(123.123)*(float(47))")


    def test_checkForSafeEquationString(self):

        self.assertTrue(self.ep.checkForSafeEquationString(" math.sqrt float ( ) * + - / . 1 2 3 4 5 6 7 8 9 0 "))

        self.assertFalse(self.ep.checkForSafeEquationString(" foo math.sqrt float ( ) * + - / . 1 2 3 4 5 6 7 8 9 0 "))


    def test_solveEquation(self):

        self.assertEqual(self.ep.solveEquation("float(5) * float(5)"), 25.0)

        self.assertFalse(self.ep.solveEquation("asdf * float(5)"))


    def test_calculateConfidence(self):

        self.assertEqual(self.ep.calculateConfidence("979-549-5150"), 80)
        self.assertEqual(self.ep.calculateConfidence("1-979-549-5150"), 70)
        self.assertEqual(self.ep.calculateConfidence("the square root of 1234"), 100)
