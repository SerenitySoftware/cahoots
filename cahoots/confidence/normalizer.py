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


class HierarchicalNormalizerChain(object):
    """
    Orchestrates the normalization of confidence values based
    on the presence of other result types.
    """

    def __init__(self, config, types, all_types):
        self.config = config
        self.types = types
        self.all_types = all_types

    def normalize(self, results):
        """Runs all normalizers against the result set"""
        for normalizer in \
                [n for n in self.config.enabled_confidence_normalizers if
                 n.test(self.types, self.all_types)]:
            results = normalizer.normalize(results)

        # returning only results that have a condfidence greater than 0
        return [res for res in results if res.confidence > 0]
