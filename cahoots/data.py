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
import yaml
import os


class DataHandler(object):
    """Handles the lookup of pieces of data from the data/ directory"""

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__)) + '/data/'

    def get_file_handle(self, filename):
        """Gets a requested file handle"""
        file_handle = open(self.path + filename, 'r')
        return file_handle

    def get_prepositions(self):
        """returns the list of prepositions"""
        if registry.test('DATA_prepositions'):
            return registry.get('DATA_prepositions')

        handle = self.get_file_handle('prepositions.yaml')
        prepositions = yaml.load(handle)
        handle.close()

        registry.set('DATA_prepositions', prepositions)
        return prepositions
