from brain.util import BrainRegistry
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import redis, redisbayes, os, glob


class BayesianTrainerChangeEventHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        ProgrammingBayesianClassifier.trainClassifier(False)


class ProgrammingBayesianClassifier:

    def __init__(self):
        if not BrainRegistry.test('PPredisBayes'):
            rb = redisbayes.RedisBayes(redis=redis.Redis())
            BrainRegistry.set('PPredisBayes', rb)
            ProgrammingBayesianClassifier.trainClassifier()


    @staticmethod
    def trainClassifier(setupWatcher=True):
        rb = BrainRegistry.get('PPredisBayes')

        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "bayes_trainers/*")

        trainers = {}

        for filePath in glob.glob(path):
            with open(filePath, 'r') as languageFile:
                language = filePath.split('.').pop()

                if language not in trainers:
                    trainers[language] = []

                trainers[language].append(languageFile.read())

        rb.flush()

        for language in trainers:
            #print language + ' ' + str(len(' '.join(trainers[language])))
            rb.train(language, ' '.join(trainers[language]))

        if setupWatcher:
            event_handler = BayesianTrainerChangeEventHandler()
            observer = Observer()
            observer.schedule(event_handler, os.path.join(directory, "bayes_trainers/"))
            observer.start()


    def classify(self, dataString):
        rb = BrainRegistry.get('PPredisBayes')

        return rb.score(dataString)
        