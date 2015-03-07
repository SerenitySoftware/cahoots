from cahoots.parsers.programming.bayesian import \
    ProgrammingBayesianClassifier
from SereneRegistry import registry
from tests.unit.config import TestConfig
from inspect import ismethod
import mock
import unittest


class RedisStub():

    Host = None
    Port = None
    Unix_socket_path = None
    Connection_pool = None

    def __init__(self, host, port, unix_socket_path, connection_pool):
        RedisStub.Host = host
        RedisStub.Port = port
        RedisStub.Unix_socket_path = unix_socket_path
        RedisStub.Connection_pool = connection_pool


class RedisBayesStub():

    Redis = None
    Tokenizer = None
    Prefix = None

    Languages = {}

    Flushed = False

    data_string = None

    def __init__(self, redis=None, tokenizer=None, prefix=None):
        RedisBayesStub.Redis = redis
        RedisBayesStub.Tokenizer = tokenizer
        RedisBayesStub.Prefix = prefix

    def train(self, language, sample):
        RedisBayesStub.Languages[language] = sample

    def flush(self):
        RedisBayesStub.Flushed = True

    def score(self, data_string):
        RedisBayesStub.data_string = data_string
        return 'FooBar'


class ProgrammingBayesianClassifierTests(unittest.TestCase):

    def setUp(self):
        registry.set('PP_redis_bayes', RedisBayesStub())

    def tearDown(self):
        registry.flush()
        RedisStub.Host = None
        RedisStub.Port = None
        RedisStub.Unix_socket_path = None
        RedisStub.Connection_pool = None
        RedisBayesStub.Redis = None
        RedisBayesStub.Tokenizer = None
        RedisBayesStub.Prefix = None
        RedisBayesStub.Languages = {}
        RedisBayesStub.Flushed = False
        RedisBayesStub.data_string = None

    @mock.patch('redis.Redis', RedisStub)
    @mock.patch('redisbayes.RedisBayes', RedisBayesStub)
    def test_bootstrapSetsUpClassifierAsExpected(self):

        ProgrammingBayesianClassifier.bootstrap(TestConfig)

        self.assertEqual(RedisStub.Host, 'localhost')
        self.assertEqual(RedisStub.Port, 6379)
        self.assertEqual(RedisStub.Unix_socket_path, None)
        self.assertEqual(RedisStub.Connection_pool, None)

        self.assertIsInstance(RedisBayesStub.Redis, RedisStub)
        self.assertTrue(ismethod(RedisBayesStub.Tokenizer))
        self.assertEqual(':', RedisBayesStub.Prefix[-1:])
        self.assertIsInstance(registry.get('PP_redis_bayes'), RedisBayesStub)
        self.assertTrue(RedisBayesStub.Flushed)

    @mock.patch('redis.Redis', RedisStub)
    @mock.patch('redisbayes.RedisBayes', RedisBayesStub)
    def test_classifierProducesExpectedResult(self):

        ProgrammingBayesianClassifier.bootstrap(TestConfig)

        classifier = ProgrammingBayesianClassifier()
        result = classifier.classify('echo "Hello World";')

        self.assertEqual('echo "Hello World";', RedisBayesStub.data_string)
        self.assertEqual('FooBar', result)

    def test_tokenizerProducesExpectedList(self):
        result = ProgrammingBayesianClassifier.bayes_tokenizer('Hello World')
        self.assertEqual(2, len(result))
