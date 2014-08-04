from cahoots.parsers.base import BaseParser
from cahoots.util import isNumber
import os, glob, yaml, string
from SereneRegistry import registry


class MeasurementParser(BaseParser):

    # to be used to determine if this is an area described using "3 square miles" etc
    areaDescriptors = ["square", "sr", "sq"]
    allowedPunctuation = ["'", '"', "."]
    integerStrings = ["quarter", "half"]
    
    allUnits = []
    systemUnits = {}

    @staticmethod
    def bootstrap():
        """Loads unit lists for use in this instance of the measurement parser"""
        allUnits = []
        systemUnits = {}

        directory = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(directory, "units/*.yaml")

        for filePath in glob.glob(path):
            with open(filePath, 'r') as unitFile:
                unitType = yaml.load(unitFile)
                allUnits.extend(unitType['keywords'])
                systemUnits[unitType['id']] = unitType

        # we're sorting all keywords by length, so we can locate the longest first and not have conflicts from the smaller.
        allUnits = sorted(set(allUnits), key=len, reverse=True)

        for systemId in systemUnits:
            systemUnits[systemId]['keywords'] = sorted(systemUnits[systemId]['keywords'], key=len, reverse=True)

        registry.set('MPallUnits', allUnits)
        registry.set('MPsystemUnits', systemUnits)


    def __init__(self):
        self.Type = "Measurement"
        self.Confidence = 50
        self.allUnits = registry.get('MPallUnits')
        self.systemUnits = registry.get('MPsystemUnits')


    def basicUnitCheck(self, data):
        """Checks to see if the data is simply a reference to a unit"""
        return data in self.allUnits


    def determineSystemUnit(self, data):
        """Determines what system this unit is a member of"""
        for systemId, systemData in self.systemUnits.items():
            if data in systemData['keywords']:
                return systemId


    def identifyUnitsInData(self, data):
        """Finds all units of measurement in a set of data"""
        matches = []

        for unit in self.allUnits:
            unitStart = data.find(unit)
            if unitStart != -1:
                #replacing the located unit with a space
                data = data[:unitStart] + ' ' + data[(unitStart+len(unit)):]

                # if we find the term again, we can't classify this as measurement.
                if data.find(unit) != -1:
                    raise Exception("Invalid Measurement Data")

                matches.append(unit)

        return data.strip(), matches


    def getSubType(self, systemId):
        """Gets a string we can set as our result subtype"""
        return self.systemUnits[systemId]['system'] + ' ' + self.systemUnits[systemId]['type']


    def parse(self, data, **kwargs):

        data = data.strip().lower()

        # If the length of the data is longer than 50...almost certainly not a measurement
        if len(data) > 50 or len(data) == 0:
            return

        #checking if the dataset IS a unit reference.
        if self.basicUnitCheck(data):
            systemId = self.determineSystemUnit(data)
            yield self.result(self.getSubType(systemId))
            return

        # If there aren't any digits or whitespace in the data, we pretty much can just eliminate it at this point
        elif not set(data).intersection(set(string.digits)) and not set(data).intersection(set(string.whitespace)):
            return

        # processing the data by identifying and removing found units from it
        try:
            data, units = self.identifyUnitsInData(data)
        except:
            return
        else:
            # if we found no units in the data, fail
            if not units:
                return

        # Turning this into a float so we can operate on it more bettererly
        self.Confidence = float(self.Confidence)


        # Finding system ids the found units belong to
        systemIds = []
        for unit in units:

            # Adding a small amount of confidence for every unit we located
            self.Confidence = self.Confidence * 1.1

            systemIds.append(self.determineSystemUnit(unit))
        systemIds = set(systemIds)

        # for every found systemId over 1, we cut our self confidence
        if len(systemIds) > 1:
            for i in systemIds:
                self.Confidence = self.Confidence * 0.75


        # if all we have left is a number, it helps our case a lot.
        if isNumber(data):
            self.Confidence += 50
        else:
            # our penalty for extra words is 25% of whatever our confidence is right now
            extraWordPenalty = self.Confidence * 0.25

            # cutting our confidence down for every unidentified word we have in the data string
            data = data.split()
            for i in data:
                # if we found a number, we dont penalize for that
                if not isNumber(i) and i not in string.punctuation:
                    self.Confidence -= extraWordPenalty

                # if we hit less than 2% confdence, we just fail.
                if int(self.Confidence) < 2:
                    return


        # If there aren't any numbers in the data, we lower the confidence.
        if not set(''.join(data)).intersection(set(string.digits)):
            print "foobar"
            self.Confidence = self.Confidence * 0.75


        # Cleaning up our final confidence number
        self.Confidence = min(100, int(round(self.Confidence)))

        # assembling a string representing the subtypes we found
        subTypes = []
        for sid in systemIds:
            subTypes.append(self.getSubType(sid))

        yield self.result(', '.join(subTypes))