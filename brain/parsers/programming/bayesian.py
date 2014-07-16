from brain.util import BrainRegistry
import config
import redis, redisbayes, os, glob, string

class ProgrammingBayesianClassifier:
    """Responsible for classifying an example of source code into a specific programming language"""

    def __init__(self):
        """Creates an instance of a bayes classifer for use in identifying programmng languages"""
        pass


    @staticmethod
    def bootstrap():
        """Trains the bayes classifier with examples from various programming languages"""
        bayesRedis = redis.Redis(
            host=config.redis['host'],
            port=config.redis['port'],
            unix_socket_path=config.redis['unix_socket_path'],
            connection_pool=config.redis['connection_pool']
        )

        rb = redisbayes.RedisBayes(redis=bayesRedis, tokenizer=ProgrammingBayesianClassifier.bayesTokenizer)

        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "bayes_trainers/*")

        trainers = {}

        for filePath in glob.glob(path):
            with open(filePath, 'r') as languageFile:
                language = filePath.split('.').pop()
                trainers[language] = languageFile.read()

        rb.flush()

        for language in trainers:
            rb.train(language, trainers[language])

        BrainRegistry.set('PPredisBayes', rb)


    @staticmethod
    def bayesTokenizer(text):
        text = text.replace('->', ' -> ')
        text = text.replace('.', ' . ')
        text = text.replace('){', ') {')
        text = text.replace('$', ' $')
        text = text.replace(':', ' $')
        text = text.replace('\\', ' \\ ')
        words = text.split()
        return [w for w in words if len(w) > 0 and w not in string.whitespace]


    def classify(self, dataString):
        """Takes an string and creates a dict of programming language match probabilities"""
        rb = BrainRegistry.get('PPredisBayes')

        return rb.score(dataString)
        