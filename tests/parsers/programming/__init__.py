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
from cahoots.parsers.programming import ProgrammingParser
from SereneRegistry import registry
from cahoots.result import ParseResult
from tests.config import TestConfig
import unittest
import mock


class ProgrammingParserTests(unittest.TestCase):

    bootstrapMock = mock.MagicMock()

    bigSpreadClassifyMock = mock.MagicMock(return_value={
        'php': -1000,
        'javascript': -1700,
        'vb': -1900,
        'cpp': -1100,
        'python': -1530,
    })

    smallSpreadClassifyMock = mock.MagicMock(return_value={
        'php': 50,
        'javascript': -5,
        'vb': 20,
        'cpp': 14,
        'python': 48,
    })

    pbcBootstrap = \
        'cahoots.parsers.programming.bayesian.' + \
        'ProgrammingBayesianClassifier.bootstrap'

    pbcClassify = \
        'cahoots.parsers.programming.bayesian.' + \
        'ProgrammingBayesianClassifier.classify'

    def tearDown(self):
        registry.flush()

    @mock.patch(pbcBootstrap, bootstrapMock)
    def test_bootstrapCarriesOutAsExpected(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        self.assertEqual(486, len(registry.get('PP_all_keywords')))
        self.assertEqual(11, len(registry.get('PP_language_keywords')))

    @mock.patch(pbcBootstrap, bootstrapMock)
    def test_find_common_tokensFindsExpectedKeywords(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)
        result = parser.find_common_tokens(['for', 'if', 'foobar'])

        self.assertEqual(2, len(result))

    @mock.patch(pbcBootstrap, bootstrapMock)
    def test_basicLanguageHeuristicFindsExpectedKeywords(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)
        result = parser.basic_language_heuristic(
            registry.get('PP_language_keywords')['php'],
            ['for', 'if', 'foobar']
        )

        self.assertEqual(2, len(result))

    def test_createDatasetReturnsExpectedList(self):
        config = TestConfig()
        parser = ProgrammingParser(config)

        self.assertEqual(
            set(['hello', 'world']),
            parser.create_dataset('Hello World')
        )

    @mock.patch(pbcBootstrap, bootstrapMock)
    def test_parseWithNoCommonTokensReturns(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)
        count = 0
        for _ in parser.parse('scoobydoo'):
            count += 1
        self.assertEqual(0, count)

    @mock.patch(pbcBootstrap, bootstrapMock)
    def test_parseWithNoLexedLanguagesReturns(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)
        count = 0
        for _ in parser.parse('m foo bar'):
            count += 1
        self.assertEqual(0, count)

    @mock.patch(pbcBootstrap, bootstrapMock)
    @mock.patch(pbcClassify, smallSpreadClassifyMock)
    def test_parse(self):
        '''tests parse with a small spread in bayesian match values'''
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)

        expected_types = [
            'Visual Basic',
            'Python',
            'PHP'
        ]

        results = []

        for result in parser.parse('with cout echo'):
            self.assertIsInstance(result, ParseResult)
            results.append(result)

        self.assertEqual(3, len(results))

        for result in results:
            self.assertIn(result.subtype, expected_types)

        self.smallSpreadClassifyMock.assert_called_once_with('with cout echo')

    def test_calculate_confidence(self):
        lex_languages = {
            'foo': 12
        }
        bayes_languages = {
            'foo': 150
        }

        result = \
            ProgrammingParser.calculate_confidence(
                lex_languages,
                bayes_languages
            )

        self.assertEqual({'foo': 100}, result)
