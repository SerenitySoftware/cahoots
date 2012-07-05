from brain.util import BrainRegistry
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import redis, redisbayes, os, glob, re, string


class BayesianTrainerChangeEventHandler(FileSystemEventHandler):
    """Responsible for reloading bayes training data if the training source directory changes"""

    def on_any_event(self, event):
        ProgrammingBayesianClassifier.trainClassifier(False)


class ProgrammingBayesianClassifier:
    """Responsible for classifying an example of source code into a specific programming language"""

    def __init__(self):
        """Creates an instance of a bayes classifer for use in identifying programmng languages"""
        if not BrainRegistry.test('PPredisBayes'):
            rb = redisbayes.RedisBayes(redis=redis.Redis(), tokenizer=self.bayesTokenizer)
            BrainRegistry.set('PPredisBayes', rb)
            ProgrammingBayesianClassifier.trainClassifier()


    @staticmethod
    def trainClassifier(setupWatcher=True):
        """Trains the bayes classifier with examples from various programming languages"""
        rb = BrainRegistry.get('PPredisBayes')

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

        if setupWatcher:
            event_handler = BayesianTrainerChangeEventHandler()
            observer = Observer()
            observer.schedule(event_handler, os.path.join(directory, "bayes_trainers/"))
            observer.start()

    @staticmethod
    def bayesTokenizer(text):
        text = text.replace('->', ' -> ')
        text = text.replace('.', ' . ')
        text = text.replace('){', ') {')
        text = text.replace('$', ' $')
        words = text.split()
        return [w for w in words if len(w) > 0 and w not in string.whitespace]


    def classify(self, dataString):
        """Takes an string and creates a dict of programming language match probabilities"""
        rb = BrainRegistry.get('PPredisBayes')

        return rb.score(dataString)
        