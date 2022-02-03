"""
Generates random data for testing
"""

import struct
import time
import serial

from constants import Constants

from DataInterfaces.data_interface_core import DataInterfaceCore

from DataInterfaces.DataInterfaceTools.annunciator_helper import AnnunciatorHelper


class GroundStationDataInterface(DataInterfaceCore):
    def __init__(self):
        super().__init__()

        self.nextCheckTime = time.time()
        self.serial_port = "/dev/ttyACM0"
        self.baud_rate = 9600
        self.connected = False
        self.has_data = False

        self.annunciator = AnnunciatorHelper()

    def spin(self):
        if self.nextCheckTime <= time.time():
            self.console_callback("Trying to connect to ground station on {}".format(self.serial_port), 0)
            try:
                self.serial = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
                self.connected = True
                self.connectedLoop()
                self.nextCheckTime = time.time() + 5
                self.serial.close()
            except IOError as e:
                self.connected = False
                self.has_data = False
                self.console_callback("Could not connect to ground station on port {}".format(self.serial_port), 2)
                # print(e)
                self.nextCheckTime = time.time() + 5

        self.updateEveryLoop()

    def connectedLoop(self):
        while self.connected and self.is_running:
            try:
                self.readData()
                time.sleep(0.01)
            except IOError:
                self.connected = False
                self.has_data = False
                self.console_callback("Lost connection to ground station on port {}".format(self.serial_port), 2)
            self.updateEveryLoop()

    def readData(self):
        raw_bytes = self.serial.readline()
        try:
            unpacked_data = struct.unpack('ffffdBBBB', raw_bytes)
            gps_lat = unpacked_data[0]
            gps_lon = unpacked_data[1]
            gps_alt = unpacked_data[2]
            baro_pres = unpacked_data[2]
            batt_voltage = unpacked_data[3]
            pyro_cont = unpacked_data[4]
            state = unpacked_data[5]
            self.data_dictionary[Constants.latitude_key] = gps_lat
            self.data_dictionary[Constants.longitude_key] = gps_lon
            self.data_dictionary[Constants.altitude_key] = gps_alt
            self.data_dictionary[Constants.barometer_pressure_key] = baro_pres
            self.data_dictionary[Constants.fcb_battery_voltage] = batt_voltage

            self.console_callback("New data: {}".format(unpacked_data), 0)

            self.has_data = True
        except struct.error as e:
            self.console_callback("Can't parse {0} (length: {2} bytes):\n{1}".format(raw_bytes, e, len(raw_bytes)), 1)

    def updateEveryLoop(self):
        if self.connected:
            self.annunciator.setAnnunciator(0, "GS Connection", 0, "Connected to ground station")
        else:
            self.annunciator.setAnnunciator(0, "GS Connection", 2, "No connection")

        if self.has_data:
            self.annunciator.setAnnunciator(1, "GS Data", 0, "Receiving data from ground station")
        else:
            self.annunciator.setAnnunciator(1, "GS Data", 2, "No data")

        self.data_dictionary["annunciator_1"] = self.annunciator.getList()

        self.data_dictionary["status"] = self.annunciator.getOverallStatus()
