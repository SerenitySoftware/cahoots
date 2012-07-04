class BrainRegister:
    '''
    A memory key/value registry
    '''

    storage = {}

    @staticmethod
    def set(key, value):
        BrainRegister.storage[key] = value

    @staticmethod
    def get(key):
        if key in BrainRegister.storage:
            return BrainRegister.storage[key]
        else:
            None