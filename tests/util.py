
def getFixtureFileContents(fileName):
    """Gets the contents of a file in the fixtures directory"""
    return open('fixtures/'+fileName, 'r').read()