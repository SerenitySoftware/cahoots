from brain.parsers.base import BaseParser
from brain.util import BrainRegistry, isNumber
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os, re, glob, yaml


class MeasurementUnitFileChangeEventHandler(FileSystemEventHandler):
    """Responsible for reloading unit data if the yaml directory changes"""

    # Static Measurement Parser Instance
    mpi = None

    def on_any_event(self, event):
        self.mpi.loadUnits(False)


class MeasurementParser(BaseParser):

    # to be used to determine if this is an area described using "3 square miles" etc
    areaDescriptors = ["square", "sr", "sq"]
    allowedPunctuation = ["'", '"', "."]
    integerStrings = ["quarter", "half"]
    
    allUnits = []
    systemUnits = {}


    def __init__(self, initUnits = True):
        self.Type = "Measurement"
        self.Confidence = 50

        if initUnits:
            self.__initUnits()


    def __initUnits(self):
        """Loads unit lists for use in this instance of the measurement parser"""

        # if we have already read in and stored the units in memory, we just pull them out of memory
        if BrainRegistry.test('MPallUnits') and BrainRegistry.test('MPsystemUnits'):
            self.allUnits = BrainRegistry.get('MPallUnits')
            self.systemUnits = BrainRegistry.get('MPsystemUnits')
            return

        # Not found....Load it!
        self.loadUnits()


    def loadUnits(self, setupWatcher=True):
        """
        Reloads units from the yaml files on disk
        Optionally sets of a watcher for changes of the yaml file directory
        """

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

        self.allUnits = sorted(set(allUnits), key=len, reverse=True)

        for systemId in systemUnits:
            systemUnits[systemId]['keywords'] = sorted(systemUnits[systemId]['keywords'], key=len, reverse=True)

        self.systemUnits = systemUnits

        BrainRegistry.set('MPallUnits', self.allUnits)
        BrainRegistry.set('MPsystemUnits', self.systemUnits)

        # Launching an observer to watch for changes to the language directory
        if setupWatcher:
            MeasurementUnitFileChangeEventHandler.mpi = MeasurementParser(False)
            event_handler = MeasurementUnitFileChangeEventHandler()
            observer = Observer()
            observer.schedule(event_handler, os.path.join(directory, "units/"))
            observer.start()


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
            return self.result(False)

        if self.basicUnitCheck(data):
            systemId = self.determineSystemUnit(data)
            return self.result(True, self.getSubType(systemId))


        # processing the data by identifying and removing found units from it
        try:
            data, units = self.identifyUnitsInData(data)
        except:
            return self.result(False)
        else:
            # if we found no units in the data, fail
            if not units:
                return self.result(False)


        # Finding system ids the found units belong to
        systemIds = []
        for unit in units:
            systemIds.append(self.determineSystemUnit(unit))
        systemIds = set(systemIds)


        # for every found systemId over 1, we cut our self confidence in half
        if len(systemIds) > 1:
            for i in systemIds:
                self.Confidence = int(round(float(self.Confidence)/2.00)) # 25, 13, 7, 4, 2, 1, 1, 1...


        # if all we have left is a number, it helps our case a lot.
        if isNumber(data):
            self.Confidence += 50
        else:
            # cutting our confidence down for every unidentified word we have in the data string
            data = data.split()
            for i in data:
                # if we found a number, we dont penalize for that
                if not isNumber(i):
                    self.Confidence = int(self.Confidence/2) # 25, 12, 6, 3, 1, 0

                # if we hit 0, we fail
                if self.Confidence == 0:
                    return self.result(False)


        # assembling a string representing the subtypes we found
        subTypes = []
        for sid in systemIds:
            subTypes.append(self.getSubType(sid))

        return self.result(True, ', '.join(subTypes))