from cahoots.parsers.programming import ProgrammingParser
from SereneRegistry import registry
from cahoots.result import ParseResult
from tests.unit.config import TestConfig
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

        self.assertEqual(486, len(registry.get('PPallKeywords')))
        self.assertEqual(11, len(registry.get('PPlanguageKeywords')))

    @mock.patch(pbcBootstrap, bootstrapMock)
    def test_findCommonTokensFindsExpectedKeywords(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)
        result = parser.findCommonTokens(['for', 'if', 'foobar'])

        self.assertEqual(2, len(result))

    @mock.patch(pbcBootstrap, bootstrapMock)
    def test_basicLanguageHeuristicFindsExpectedKeywords(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)
        result = parser.basicLanguageHeuristic(
            'php',
            registry.get('PPlanguageKeywords')['php'],
            ['for', 'if', 'foobar']
        )

        self.assertEqual(2, len(result))

    def test_createDatasetReturnsExpectedList(self):
        config = TestConfig()
        parser = ProgrammingParser(config)

        self.assertEqual(
            set(['hello', 'world']),
            parser.createDataset('Hello World')
        )

    @mock.patch(pbcBootstrap, bootstrapMock)
    def test_parseWithNoCommonTokensReturns(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)
        for result in parser.parse('scoobydoo'):
            self.assertTrue(False)

    @mock.patch(pbcBootstrap, bootstrapMock)
    def test_parseWithNoLexedLanguagesReturns(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)
        for result in parser.parse('m foo bar'):
            self.assertTrue(False)

    @mock.patch(pbcBootstrap, bootstrapMock)
    @mock.patch(pbcClassify, bigSpreadClassifyMock)
    def test_parseWithLargeDeepNegativeSpread(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)

        expectedTypes = (
            'Visual Basic',
            'JavaScript',
            'ActionScript',
            'Python',
            'PHP'
        )

        results = []

        for result in parser.parse('with cout echo'):
            self.assertIsInstance(result, ParseResult)
            results.append(result)

        self.assertEqual(5, len(results))

        for result in results:
            self.assertIn(result.Subtype, expectedTypes)

        self.bigSpreadClassifyMock.assert_called_once_with('with cout echo')

    @mock.patch(pbcBootstrap, bootstrapMock)
    @mock.patch(pbcClassify, smallSpreadClassifyMock)
    def test_parseWithSmallSpread(self):
        config = TestConfig()
        ProgrammingParser.bootstrap(config)
        self.bootstrapMock.assert_called_with(config)

        parser = ProgrammingParser(config)

        expectedTypes = (
            'Visual Basic',
            'JavaScript',
            'ActionScript',
            'Python',
            'PHP'
        )

        results = []

        for result in parser.parse('with cout echo'):
            self.assertIsInstance(result, ParseResult)
            results.append(result)

        self.assertEqual(5, len(results))

        for result in results:
            self.assertIn(result.Subtype, expectedTypes)

        self.smallSpreadClassifyMock.assert_called_once_with('with cout echo')
