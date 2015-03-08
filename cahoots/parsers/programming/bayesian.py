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
import redis
import redisbayes
import os
import glob
import string
import time


class ProgrammingBayesianClassifier(object):
    """
    Responsible for classifying an example of source
    code into a specific programming language
    """

    @staticmethod
    def bootstrap(config):
        """
        Trains the bayes classifier with examples
        from various programming languages
        """
        bayes_redis = redis.Redis(
            host=config.redis['host'],
            port=config.redis['port'],
            unix_socket_path=config.redis['unix_socket_path'],
            connection_pool=config.redis['connection_pool']
        )

        namespace = str(time.time())+':'

        classifier = redisbayes.RedisBayes(
            redis=bayes_redis,
            tokenizer=ProgrammingBayesianClassifier.bayes_tokenizer,
            prefix=namespace
        )

        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "bayes_trainers/*")

        trainers = {}

        for file_path in glob.glob(path):
            with open(file_path, 'r') as language_file:
                language = file_path.split('.').pop()
                trainers[language] = language_file.read()

        for language in trainers:
            classifier.train(language, trainers[language])

        old_rb = registry.get('PP_redis_bayes')

        registry.set('PP_redis_bayes', classifier)

        # Getting rid of the old namespaced data.
        if old_rb:
            old_rb.flush()

    @staticmethod
    def bayes_tokenizer(text):
        """Breaks a string down into tokens for our classifier"""
        text = text.replace('->', ' -> ')
        text = text.replace('.', ' . ')
        text = text.replace('){', ') {')
        text = text.replace('$', ' $')
        text = text.replace(':', ' :')
        text = text.replace('\\', ' \\ ')
        words = text.split()
        return [w for w in words if len(w) > 0 and w not in string.whitespace]

    @classmethod
    def classify(cls, data_string):
        """
        Takes an string and creates a dict of
        programming language match probabilities
        """
        classifier = registry.get('PP_redis_bayes')

        return classifier.score(data_string)
