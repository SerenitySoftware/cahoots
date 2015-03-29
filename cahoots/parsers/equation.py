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
# pylint: disable=eval-used
from phonenumbers.phonenumberutil import NumberParseException
from cahoots.parsers.base import BaseParser
from cahoots.util import is_number
from phonenumbers import phonenumberutil
import re
import string
# pylint: disable=unused-import
import math  # flake8: noqa


class EquationParser(BaseParser):
    """determines if given data is a mathematical equation"""

    # After we've processed the input string from the user,
    # this var will contain the assembled result
    parsed_equation = None

    def __init__(self, config):
        BaseParser.__init__(self, config, "Equation", 100)

    def is_simple_equation(self, data):
        """checking if only has symbols found in simple math equations"""

        rgx = re.compile(r"""^
           ([()*.\-+0-9^/ ])*
           $""", re.VERBOSE)

        if rgx.match(data):
            data = self.auto_float(data)
            self.parsed_equation = self.auto_multiply(data)
            return True

        return False

    def is_text_equation(self, data):
        """Searching for specific textual markers that can be converted"""

        # SQUARE ROOTS
        parsed_data = re.compile(
            r'SQUARE[ ]{1,}ROOT[ ]{1,}OF[ ]{1,}\d+(\.\d+)?'
        ).sub(self.square_root_text_replace, data)

        # Simple Operators
        parsed_data = parsed_data.replace('TIMES', '*')
        parsed_data = parsed_data.replace('PLUS', '+')
        parsed_data = parsed_data.replace('MINUS', '-')
        parsed_data = parsed_data.replace('DIVIDED BY', '/')
        parsed_data = parsed_data.replace('DIVIDEDBY', '/')

        # Simple Powers
        parsed_data = re.compile(
            '[ ]{1,}SQUARED|[ ]{1,}CUBED'
        ).sub(self.simple_power_replace, parsed_data)

        if parsed_data != data:
            parsed_data = self.auto_float(parsed_data)
            self.parsed_equation = self.auto_multiply(parsed_data)
            return True

        return False

    @classmethod
    def simple_power_replace(cls, match):
        """Converts "SQUARED" and "CUBED" to their proper exponent form"""

        my_string = match.group()

        if my_string.find('SQUARED') != -1:
            my_string = '**2'
        elif my_string.find('CUBED') != -1:
            my_string = '**3'

        return my_string

    @classmethod
    def square_root_text_replace(cls, match):
        """Replaces square root references with math.sqrt"""

        my_string = match.group().replace('SQUARE', '')
        my_string = my_string.replace('ROOT', '')
        my_string = my_string.replace('OF', '')
        my_string = my_string.strip()

        my_string = 'math.sqrt('+my_string+')'

        return my_string

    def auto_float(self, data):
        """Makes all digits/decimals into floats to prevent auto-rounding"""

        data = re.compile(r'\d+(\.\d+)?').sub(self.float_replace, data)

        return data

    @classmethod
    def float_replace(cls, match):
        """
        This turns our numbers into floats before we eval the equation.
        This is because 4/5 comes out at 0, etc. Python is strongly typed...
        """
        result = 'float('+match.group()+')'
        return result

    @classmethod
    def auto_multiply(cls, data):
        """
        Any back to back parens/floats can be assumed to be
        multiplication. Adding * operator between them
        """
        data = data.replace(')float', ')*float')
        data = data.replace(')(', ')*(')

        return data

    @classmethod
    def check_for_safe_equation_string(cls, equation):
        """
        Checks to make sure that the equation
        doesn't contain any unexpected characters

        This is pseudo-sanitization. We just make sure that the string has
        only "safe" characters. we do this by removing all expected strings,
        and seeing if we have nothing left.
        """

        # These are characters or strings that we can use in an equation
        safe_strings = \
            ['math.sqrt', 'float', '(', ')', '*', '+', '-', '/', '.']

        for safe_string in safe_strings:
            equation = equation.replace(safe_string, '')

        for num in range(10):
            equation = equation.replace(str(num), '')

        equation = equation.strip()

        return '' == equation

    def solve_equation(self, equation):
        """Sanitizes and Evaluates the equation to see if it's solve-able"""

        if not self.check_for_safe_equation_string(equation):
            return False

        try:
            return eval(equation.strip())
        except (AttributeError, SyntaxError, TypeError):
            self.confidence = 0
            return False

    @classmethod
    def calculate_confidence(cls, data):
        """Calculates a confidence rating for this (possible) equation"""
        # We start with 100% confidence, and
        # then lower our confidence if needed.
        confidence = 100

        # lowering confidence if we have a phone number
        try:
            if len(data) <= 30 and len(data) >= 7:
                phonenumberutil.parse(data, _check_region=False)
                for _ in [c for c in data if c in string.punctuation]:
                    confidence -= 10
        except NumberParseException:
            pass

        return confidence

    @classmethod
    def clean_data(cls, data):
        """Removes and replaces data in prep for equation parsing"""
        clean_data = data.upper()
        clean_data = clean_data.replace('X', '*')
        clean_data = clean_data.replace('^', '**')
        clean_data = clean_data.replace('THE', '')
        clean_data = clean_data.strip()
        return clean_data

    def parse(self, data):
        """
        Standard parse function for checking if
        entered string is a mathematical equation
        """

        # if we just have a number, we know this isn't an equation
        if is_number(data):
            return

        # Doing some initial data cleanup
        clean_data = self.clean_data(data)

        if not clean_data:
            return

        if self.is_simple_equation(clean_data):
            result_type = "Simple"
        elif self.is_text_equation(clean_data):
            result_type = "Text"
        else:
            return

        # If the equation proves to be solveable, we
        # calculate a confidence and report success
        calculated = self.solve_equation(self.parsed_equation)
        if calculated:
            yield self.result(
                result_type,
                self.calculate_confidence(data),
                calculated
            )
