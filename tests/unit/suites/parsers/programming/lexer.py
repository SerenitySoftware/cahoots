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
# pylint: disable=invalid-name,too-many-public-methods,missing-docstring
from cahoots.parsers.programming.lexer import \
    ProgrammingLexerThread, \
    ProgrammingLexer
from pygments.lexers.web import PhpLexer
import unittest


class ProgrammingLexerThreadTests(unittest.TestCase):

    def test_phpLexerDetectsExpectedTokens(self):
        data_string = "echo 'Hello World';"
        lexer = ProgrammingLexerThread(
            'php',
            PhpLexer(startinline=True),
            data_string
        )

        lexer.start()
        lexer.join()

        self.assertEqual(3, lexer.result)

    def test_phpLexerDetectsExpectedNoTokens(self):
        data_string = " "
        lexer = ProgrammingLexerThread(
            'php',
            PhpLexer(startinline=True),
            data_string
        )

        lexer.start()
        lexer.join()

        self.assertFalse(lexer.result)


class ProgrammingLexerTests(unittest.TestCase):

    def test_phpIsDetectedUsingProgrammingLexer(self):
        data_string = "echo 'Hello World';"
        lexer = ProgrammingLexer(['php'], data_string)
        result = lexer.lex()

        self.assertEqual({'php': 3}, result)
