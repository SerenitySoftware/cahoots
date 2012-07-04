class BrainRegistry:
    '''
    A memory key/value registry
    '''

    storage = {}

    @staticmethod
    def set(key, value):
        BrainRegistry.storage[key] = value

    @staticmethod
    def get(key):
        if key in BrainRegistry.storage:
            return BrainRegistry.storage[key]
        else:
            None

    @staticmethod
    def test(key):
        return key in BrainRegistry.storage