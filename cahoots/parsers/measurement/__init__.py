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
from cahoots.parsers.base import BaseParser
from cahoots.util import is_number
from SereneRegistry import registry
import os
import glob
import yaml
import string


class MeasurementParser(BaseParser):

    """
    to be used to determine if this is an area
    described using "3 square miles" etc
    """
    areaDescriptors = ["square", "sr", "sq"]
    allowedPunctuation = ["'", '"', "."]
    integerStrings = ["quarter", "half"]

    all_units = []
    system_units = {}

    @staticmethod
    def bootstrap(config):
        """
        Loads unit lists for use in this instance of the measurement parser
        """
        all_units = []
        system_units = {}

        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "units/*.yaml")

        for file_path in glob.glob(path):
            unit_file = open(file_path, 'r')
            unit_type = yaml.load(unit_file)
            all_units.extend(unit_type['keywords'])
            system_units[unit_type['id']] = unit_type

        # we're sorting all keywords by length, so we can locate the
        # longest first and not have conflicts from the smaller.
        all_units = sorted(set(all_units), key=len, reverse=True)

        for system_id in system_units:
            system_units[system_id]['keywords'] = sorted(
                system_units[system_id]['keywords'], key=len, reverse=True
            )

        registry.set('MP_all_units', all_units)
        registry.set('MP_system_units', system_units)

    def __init__(self, config):
        BaseParser.__init__(self, config, "Measurement", 50)
        self.all_units = registry.get('MP_all_units')
        self.system_units = registry.get('MP_system_units')

    def basic_unit_check(self, data):
        """Checks to see if the data is simply a reference to a unit"""
        return data in self.all_units

    def determine_system_unit(self, data):
        """Determines what system this unit is a member of"""
        for system_id, system_data in self.system_units.items():
            if data in system_data['keywords']:
                return system_id

    def identify_units_in_data(self, data):
        """Finds all units of measurement in a set of data"""
        matches = []

        for unit in self.all_units:
            unit_start = data.find(unit)
            if unit_start != -1:

                # if this was found in the middle of a word, it's not a unit
                if (data[unit_start-1] >= 0 and
                        data[unit_start-1] in string.letters) or \
                    (data[unit_start-1] <= len(data) and
                     data[unit_start+len(unit)] in string.letters):
                    raise StandardError("Invalid Measurement Data")

                # replacing the located unit with a space
                data = data[:unit_start] + ' ' + data[(unit_start+len(unit)):]

                # if we find the term again, we can't
                # classify this as measurement.
                if data.find(unit) != -1:
                    raise StandardError("Invalid Measurement Data")

                matches.append(unit)

        return data.strip(), matches

    def get_sub_type(self, system_id):
        """Gets a string we can set as our result subtype"""
        subtype = self.system_units[system_id]['system'] + ' ' +\
            self.system_units[system_id]['type']
        return subtype

    def get_measurement_system_ids(self, data, units):
        """
        Gets the measurement systems that this data belongs to
        as well as calculating our confidence
        """

        # Turning this into a float so we can operate on it more bettererly
        self.confidence = float(self.confidence)

        # Finding system ids the found units belong to
        system_ids = []
        for unit in units:

            # Adding a small amount of confidence for every unit we located
            self.confidence = self.confidence * 1.1

            system_ids.append(self.determine_system_unit(unit))
        system_ids = set(system_ids)

        # for every found system_id over 1, we cut our self confidence
        if len(system_ids) > 1:
            for i in system_ids:
                self.confidence = self.confidence * 0.75

        # if all we have left is a number, it helps our case a lot.
        if is_number(data):
            self.confidence += 50
        else:
            # our penalty for extra words is 25% of
            # whatever our confidence is right now
            extra_word_penalty = self.confidence * 0.25

            # cutting our confidence down for every unidentified
            # word we have in the data string
            data = data.split()
            for i in data:
                # if we found a number, we dont penalize for that
                if not is_number(i) and i not in string.punctuation:
                    self.confidence -= extra_word_penalty

                # if we hit less than 2% confidence, we just fail.
                if int(self.confidence) < 2:
                    raise StandardError("Confidence Too Low")

        # If there aren't any numbers in the data, we lower the confidence.
        if not set(''.join(data)).intersection(set(string.digits)):
            self.confidence = self.confidence * 0.75

        # Cleaning up our final confidence number
        self.confidence = min(100, int(round(self.confidence)))

        return system_ids

    def parse(self, data):

        data = data.strip().lower()

        # If the length of the data is longer than 50...
        # almost certainly not a measurement
        if len(data) > 50 or len(data) == 0:
            return

        # checking if the dataset IS a unit reference.
        if self.basic_unit_check(data):
            system_id = self.determine_system_unit(data)
            yield self.result(self.get_sub_type(system_id))
            return

        # If there aren't any digits or whitespace in the data,
        # we pretty much can just eliminate it at this point
        if not set(data).intersection(set(string.digits)) and \
                not set(data).intersection(set(string.whitespace)):
            return

        # processing the data by identifying and removing found units from it
        try:
            data, units = self.identify_units_in_data(data)
        except StandardError:
            return
        else:
            # if we found no units in the data, fail
            if not units:
                return

        # Determining what measurement systems have been detected
        try:
            system_ids = self.get_measurement_system_ids(data, units)
        except StandardError:
            return

        # yielding the subtypes we found
        for sid in system_ids:
            yield self.result(self.get_sub_type(sid))
