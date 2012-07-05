class BrainRegistry:
    """A memory key/value registry"""

    storage = {}

    @staticmethod
    def set(key, value):
        """Sets a value in the registry"""
        BrainRegistry.storage[key] = value

    @staticmethod
    def get(key):
        """Gets a value from the registry"""
        if key in BrainRegistry.storage:
            return BrainRegistry.storage[key]
        else:
            None

    @staticmethod
    def test(key):
        """Checks to see if there's a key in the registry"""
        return key in BrainRegistry.storage

    @staticmethod
    def flush():
        """Removes all values from the registry"""
        BrainRegistry.storage = {}


def truncateText(text, limit=80):
    if len(text) > limit:
        text = text[:limit-3] + "..."
    return text