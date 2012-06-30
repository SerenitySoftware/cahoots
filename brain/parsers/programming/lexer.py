from pygments.lexers.agile import PerlLexer, PythonLexer, RubyLexer
from pygments.lexers.compiled import CLexer, CppLexer
from pygments.lexers.dotnet import CSharpLexer, VbNetLexer
from pygments.lexers.jvm import JavaLexer
from pygments.lexers.web import ActionScript3Lexer, PhpLexer, JavascriptLexer
from pygments import lex
from pygments.token import Token

class ProgrammingLexer:

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

    matchedLanguages = []
    data = None


    def __init__(self, matchedLangs, dataString):

        self.matchedLanguages = matchedLangs
        self.data = dataString


    def lex(self):
        '''
        For every possible matched language, we run a lexer to see if we can eliminate
        it as a possible match. If we detect errors, or have no lexer matches, we remove it from the list.
        TODO: Multithread this?
        '''

        results = {}
        
        # Looping through each matched language that has a lexer
        for lexerId, lexer in [[lexid, lxr] for lexid, lxr in self.lexers.items() if lexid in self.matchedLanguages]:

            # lexing the data to see what lexers can tokenize it
            tokens = [tok for tok, text in lex(self.data, lexer) if (tok != Token.Text and text != '')]
            tokenCount = len(tokens)

            # Errors mean we definitely didn't find the right language
            if Token.Error in tokens or tokenCount == 0:
                continue

            # Storing how many recognized tokens we have, if any
            results[lexerId] = tokenCount

        return results