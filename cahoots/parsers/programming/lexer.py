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
from pygments.lexers.agile import PerlLexer, PythonLexer, RubyLexer
from pygments.lexers.compiled import CLexer, CppLexer
from pygments.lexers.dotnet import CSharpLexer, VbNetLexer
from pygments.lexers.jvm import JavaLexer
from pygments.lexers.web import ActionScript3Lexer, PhpLexer, JavascriptLexer
from pygments import lex
from pygments.token import Token
import threading


class ProgrammingLexerThread(threading.Thread):
    """Represents a thread that will handle one parser parsing request"""
    lexer = None
    data_string = None
    result = None

    def __init__(self, lexer_id, lexer, data_string):
        self.thread_id = lexer_id
        self.lexer = lexer
        self.data_string = data_string
        threading.Thread.__init__(self)

    def run(self):
        """
        Lexes the data to see what lexers can tokenize it.
        Any successful lexers are considered possible matches.
        """
        bad_tokens = (Token.Text, Token.Name, Token.Name.Other)
        tokens = [tok for tok, text in lex(self.data_string, self.lexer)
                  if tok not in bad_tokens and text != '']
        token_count = len(tokens)

        # Errors mean we definitely didn't find the right language
        if Token.Error in tokens or token_count == 0:
            self.result = False
        else:
            self.result = token_count


class ProgrammingLexer(object):
    """lexes a string with multiple programming lexers and returns tokens"""

    lexers = {
        'actionscript': ActionScript3Lexer(),
        'c': CLexer(),
        'cpp': CppLexer(),
        'cs': CSharpLexer(),
        'java': JavaLexer(),
        'javascript': JavascriptLexer(),
        'perl': PerlLexer(),
        'php': PhpLexer(startinline=True),
        'python': PythonLexer(),
        'ruby': RubyLexer(),
        'vb': VbNetLexer(),
    }

    matched_languages = []
    data = None

    def __init__(self, matched_langs, data_string):
        self.matched_languages = matched_langs
        self.data = data_string

    def lex(self):
        """
        For every possible matched language, we run a lexer to see if we can
        eliminate it as a possible match. If we detect errors, or have no
        lexer matches, we remove it from the list.
        """

        results = {}
        threads = []

        # Looping through each matched language that has a lexer
        for lexer_id, lexer in \
                [[lexid, lxr] for lexid, lxr in
                 self.lexers.items() if lexid in self.matched_languages]:
            # Creating a thread for each lexer
            thread = ProgrammingLexerThread(lexer_id, lexer, self.data)
            thread.start()
            threads.append(thread)

        for thr in threads:
            thr.join()

        for thr in [th for th in threads if th.result]:
            results[thr.thread_id] = thr.result

        return results
