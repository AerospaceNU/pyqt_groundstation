"""
Generates random data for testing
"""

import struct
import time
import serial

from constants import Constants

from DataInterfaces.MessageParsing import fcb_message_parsing
from DataInterfaces.data_interface_core import DataInterfaceCore
from DataInterfaces.DataInterfaceTools.annunciator_helper import AnnunciatorHelper
from DataInterfaces.DataInterfaceTools.diagnostics_box_helper import DiagnosticsBoxHelper


class GroundStationDataInterface(DataInterfaceCore):
    def __init__(self):
        super().__init__()

        self.nextCheckTime = time.time()
        self.serial_port = "/dev/ttyACM0"
        self.baud_rate = 9600
        self.connected = False
        self.has_data = False
        self.good_fcb_data = False

        self.has_lat_an_lon = False

        self.last_good_data_time = 0
        self.last_data_time = 0

        self.annunciator = AnnunciatorHelper()
        self.diagnostics_box_helper = DiagnosticsBoxHelper()

    def spin(self):
        if self.nextCheckTime <= time.time():
            self.logToConsole("Trying to connect to ground station on {}".format(self.serial_port), 0)
            try:
                self.serial = serial.Serial(self.serial_port, self.baud_rate, timeout=0.05)  # Set the serial port timeout really small, so we only get one message at a time
                self.connected = True
                self.connectedLoop()
                self.nextCheckTime = time.time() + 5
                self.serial.close()
            except IOError as e:
                self.logToConsole("Could not connect to ground station on port {}".format(self.serial_port), 2)
                # print(e)
                self.nextCheckTime = time.time() + 5

        self.connected = False
        self.has_data = False
        self.good_fcb_data = False

        self.updateEveryLoop()

    def connectedLoop(self):
        while self.connected and self.should_be_running:
            try:
                self.readData()
                time.sleep(0.01)
                if time.time() - self.last_data_time > 5:  # Timeout checks on any data, not just good data
                    self.logToConsoleAndCheck("Ground station on port {} timed out".format(self.serial_port), 2)
                    self.has_data = False
                    self.good_fcb_data = False
            except IOError:
                self.logToConsole("Lost connection to ground station on port {}".format(self.serial_port), 2)
                self.connected = False
            self.updateEveryLoop()

    def readData(self):
        raw_bytes = self.serial.read(50)  # Read in bytes
        if len(raw_bytes) == 0:  # If it didn't send a message, we don't parse
            return

        self.last_data_time = time.time()

        try:
            [success, dictionary, message_type] = fcb_message_parsing.parse_fcb_message(raw_bytes)
            if success:
                self.logToConsole("New [{0}] message".format(message_type), 0)
                self.data_dictionary.update(dictionary)
                self.diagnostics_box_helper.updatePanel(message_type, dictionary)

                if message_type != "Ground Station Status":  
                    self.last_good_data_time = time.time()
                    self.good_fcb_data = True
            else:
                self.logToConsole("Could not parse message: {0}".format(message_type), 1)
                self.good_fcb_data = False

            self.has_data = True
        except struct.error as e:
            self.logToConsole("Can't parse message (length: {2} bytes):\n{1}".format(raw_bytes, e, len(raw_bytes)), 1)

    def updateEveryLoop(self):
        if self.connected:
            self.annunciator.setAnnunciator(0, "GS Connection", 0, "Connected to ground station")
        else:
            self.annunciator.setAnnunciator(0, "GS Connection", 2, "No connection")

        if self.has_data:
            self.annunciator.setAnnunciator(1, "FCB Data", 0, "Receiving data from rocket")
        else:
            self.annunciator.setAnnunciator(1, "FCB Data", 2, "No data from rocket")

        if self.good_fcb_data:
            self.annunciator.setAnnunciator(2, "Good FCB Data", 0, "FCB data current")
        else:
            self.annunciator.setAnnunciator(2, "Good FCB Data", 2, "FCB data timed out")

        self.data_dictionary["annunciator_1"] = self.annunciator.getList()

        self.data_dictionary["status"] = self.annunciator.getOverallStatus()
        self.data_dictionary[Constants.raw_message_data_key] = self.diagnostics_box_helper.get_diagnostics_dict()

        self.data_dictionary[Constants.message_age_key] = round(time.time() - self.last_good_data_time, 3)
