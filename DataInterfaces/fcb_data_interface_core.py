"""
Contains common functions to handle parsed data from the fcb
"""

import time

from constants import Constants

from DataInterfaces.data_interface_core import DataInterfaceCore
from DataInterfaces.DataInterfaceTools.annunciator_helper import AnnunciatorHelper
from DataInterfaces.DataInterfaceTools.diagnostics_box_helper import DiagnosticsBoxHelper
from DataInterfaces.DataInterfaceTools.gps_position_filter import GPSPositionFilter
from DataInterfaces.MessageParsing import fcb_message_parsing

from data_helpers import get_value_from_dictionary


class FCBDataInterfaceCore(DataInterfaceCore):
    def __init__(self):
        super().__init__()

        self.connected = False
        self.has_data = False
        self.good_fcb_data = False
        self.good_radio_crc = False

        self.has_lat_and_lon = False

        self.last_good_data_time = 0
        self.last_data_time = 0

        self.annunciator = AnnunciatorHelper()
        self.diagnostics_box_helper = DiagnosticsBoxHelper()
        self.vehicle_position_filter = GPSPositionFilter("FCB")
        self.ground_station_position_filter = GPSPositionFilter("Ground Station")  # Not used yet

    def spin(self):
        self.connected = False
        self.has_data = False
        self.good_fcb_data = False

        self.updateEveryLoop()

    def handleParsedData(self, message_type, dictionary):
        self.diagnostics_box_helper.updatePanel(message_type, dictionary)  # Update the diagnostics box with the unfiltered data

        if Constants.crc_key in dictionary:
            self.good_radio_crc = str(dictionary[Constants.crc_key]).lower() == "good"

        # Special parse operations to deal with filtering lat and lon data
        if Constants.latitude_key in dictionary and Constants.longitude_key in dictionary:  # If dictionary contains vehicle gps position, filter it
            self.vehicle_position_filter.new_gps_coords(dictionary[Constants.latitude_key], dictionary[Constants.longitude_key])
            [new_lat, new_lon] = self.vehicle_position_filter.get_filtered_position_output()
            dictionary[Constants.latitude_key] = new_lat
            dictionary[Constants.longitude_key] = new_lon

        # Filter ground station lat and lon
        if Constants.ground_station_latitude_key in dictionary and Constants.ground_station_longitude_key in dictionary:
            self.ground_station_position_filter.new_gps_coords(dictionary[Constants.ground_station_latitude_key], dictionary[Constants.ground_station_longitude_key])
            [new_lat, new_lon] = self.ground_station_position_filter.get_filtered_position_output()
            dictionary[Constants.ground_station_latitude_key] = new_lat
            dictionary[Constants.ground_station_longitude_key] = new_lon

        self.data_dictionary.update(dictionary)

        if not fcb_message_parsing.is_ground_station_message(message_type):
            self.last_good_data_time = time.time()
            self.good_fcb_data = True

    def updateEveryLoop(self):
        if self.last_good_data_time < time.time() - 5 and self.has_data:
            self.has_data = False
            self.good_fcb_data = False
            self.logToConsoleAndCheck("FCB Data Timed out", 1)

        if self.connected:
            self.annunciator.setAnnunciator(0, "GS Connection", 0, "Connected to ground station")
        else:
            self.annunciator.setAnnunciator(0, "GS Connection", 2, "No connection")

        if self.has_data:
            self.annunciator.setAnnunciator(1, "FCB Data", 0, "Receiving data from rocket")
        else:
            self.annunciator.setAnnunciator(1, "FCB Data", 2, "No data from rocket")

        if not self.good_fcb_data:
            self.annunciator.setAnnunciator(2, "Good FCB Data", 2, "FCB data timed out")
        elif not self.good_radio_crc:
            self.annunciator.setAnnunciator(2, "Good FCB Data", 1, "Bad CRC on last packet")
        else:
            self.annunciator.setAnnunciator(2, "Good FCB Data", 0, "FCB data current")

        if self.vehicle_position_filter.has_gps_data():
            self.annunciator.setAnnunciator(3, "FCB GPS Fix", 0, "Valid GPS Fix")
        else:
            self.annunciator.setAnnunciator(3, "FCB GPS Fix", 1, "No GPS Fix")

        if self.ground_station_position_filter.has_gps_data():
            self.annunciator.setAnnunciator(4, "GS GPS Fix", 0, "Valid GPS Fix")
        else:
            self.annunciator.setAnnunciator(4, "GS GPS Fix", 1, "No GPS Fix")

        self.data_dictionary["annunciator_1"] = self.annunciator.getList()

        self.data_dictionary["status"] = self.annunciator.getOverallStatus()
        self.data_dictionary[Constants.raw_message_data_key] = self.diagnostics_box_helper.get_diagnostics_dict()

        self.data_dictionary[Constants.message_age_key] = round(time.time() - self.last_good_data_time, 3)
