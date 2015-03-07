from cahoots.parsers.programming.lexer import \
    ProgrammingLexerThread, \
    ProgrammingLexer
from pygments.lexers.web import PhpLexer
import unittest


class ProgrammingLexerThreadTests(unittest.TestCase):

    def test_phpLexerDetectsExpectedTokens(self):
        dataString = "echo 'Hello World';"
        lexer = ProgrammingLexerThread(
            'php',
            PhpLexer(startinline=True),
            dataString
        )

        lexer.start()
        lexer.join()

        self.assertEqual(3, lexer.result)

    def test_phpLexerDetectsExpectedNoTokens(self):
        dataString = " "
        lexer = ProgrammingLexerThread(
            'php',
            PhpLexer(startinline=True),
            dataString
        )

        lexer.start()
        lexer.join()

        self.assertFalse(lexer.result)


class ProgrammingLexerTests(unittest.TestCase):

    def test_phpIsDetectedUsingProgrammingLexer(self):
        dataString = "echo 'Hello World';"
        lexer = ProgrammingLexer(['php'], dataString)
        result = lexer.lex()

        self.assertEqual({'php': 3}, result)
