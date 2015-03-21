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
from cahoots.parsers.programming.bayesian import \
    ProgrammingBayesianClassifier
from SereneRegistry import registry
from tests.config import TestConfig
from inspect import ismethod
import mock
import unittest


class SimpleBayesStub(object):

    Redis = None
    Tokenizer = None
    Prefix = None

    Languages = {}

    Flushed = False

    data_string = None

    def __init__(self, tokenizer=None):
        SimpleBayesStub.Tokenizer = tokenizer

    @classmethod
    def train(cls, language, sample):
        SimpleBayesStub.Languages[language] = sample

    @classmethod
    def score(cls, data_string):
        SimpleBayesStub.data_string = data_string
        return 'FooBar'


class ZipFileStub(object):

    called = []

    def __init__(self, filename, filemode):
        filename = filename.split('/').pop()
        ZipFileStub.called.append('init-' + filename + '-' + filemode)

    @classmethod
    def namelist(cls):
        ZipFileStub.called.append('namelist')
        return ['foo.def', 'bar.def']

    @classmethod
    def read(cls, filename):
        ZipFileStub.called.append('read-' + filename)
        return filename + '-text'


class ProgrammingBayesianClassifierTests(unittest.TestCase):

    def setUp(self):
        registry.set('PP_bayes', SimpleBayesStub())

    def tearDown(self):
        registry.flush()
        SimpleBayesStub.Tokenizer = None
        SimpleBayesStub.Languages = {}
        SimpleBayesStub.data_string = None
        ZipFileStub.called = []

    @mock.patch('simplebayes.SimpleBayes', SimpleBayesStub)
    @mock.patch('zipfile.ZipFile', ZipFileStub)
    def test_bootstrapSetsUpClassifierAsExpected(self):

        ProgrammingBayesianClassifier.bootstrap(TestConfig)

        self.assertEqual(
            ZipFileStub.called,
            [
                'init-trainers.zip-r',
                'namelist',
                'read-foo.def',
                'read-bar.def'
            ]
        )

        self.assertTrue(ismethod(SimpleBayesStub.Tokenizer))
        self.assertIsInstance(registry.get('PP_bayes'), SimpleBayesStub)

        self.assertEqual(
            SimpleBayesStub.Languages,
            {
                'foo': 'foo.def-text',
                'bar': 'bar.def-text'
            }
        )

    @mock.patch('simplebayes.SimpleBayes', SimpleBayesStub)
    def test_classifierProducesExpectedResult(self):

        ProgrammingBayesianClassifier.bootstrap(TestConfig)

        classifier = ProgrammingBayesianClassifier()
        result = classifier.classify('echo "Hello World";')

        self.assertEqual('echo "Hello World";', SimpleBayesStub.data_string)
        self.assertEqual('FooBar', result)

    def test_tokenizerProducesExpectedList(self):
        result = ProgrammingBayesianClassifier.bayes_tokenizer('Hello World')
        self.assertEqual(2, len(result))
