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
from SereneRegistry import registry
import simplebayes
import zipfile
import os


class ProgrammingBayesianClassifier(object):
    """
    Responsible for classifying an example of source
    code into a specific programming language
    """

    @staticmethod
    # pylint: disable=unused-argument
    def bootstrap(config):
        """
        Trains the bayes classifier with examples
        from various programming languages
        """
        classifier = simplebayes.SimpleBayes(
            ProgrammingBayesianClassifier.bayes_tokenizer
        )

        directory = os.path.dirname(os.path.abspath(__file__))

        trainers = {}

        trainer_zip = zipfile.ZipFile(directory + '/trainers.zip', 'r')
        for filename in trainer_zip.namelist():
            language = filename.split('.')[0]
            trainers[language] = trainer_zip.read(filename)

        for language in trainers:
            classifier.train(language, trainers[language])

        registry.set('PP_bayes', classifier)

    @staticmethod
    def bayes_tokenizer(text):
        """Breaks a string down into tokens for our classifier"""
        text = text.replace('->', ' -> ')
        text = text.replace('.', ' . ')
        text = text.replace(')', ' ) ')
        text = text.replace('(', ' ( ')
        text = text.replace('{', ' { ')
        text = text.replace('}', ' } ')
        text = text.replace('[', ' [ ')
        text = text.replace(']', ' ] ')
        text = text.replace('$', ' $ ')
        text = text.replace(':', ' : ')
        text = text.replace('\\', ' \\ ')
        return text.split()

    @classmethod
    def classify(cls, data_string):
        """
        Takes an string and creates a dict of
        programming language match probabilities
        """
        classifier = registry.get('PP_bayes')

        return classifier.score(data_string)
