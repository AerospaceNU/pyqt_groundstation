import time

from src.constants import Constants
from src.Modules.data_interface_core import ThreadedModuleCore
from src.Modules.DataInterfaceTools.annunciator_helper import AnnunciatorHelper
from src.Modules.DataInterfaceTools.diagnostics_box_helper import DiagnosticsBoxHelper
from src.Modules.DataInterfaceTools.gps_position_filter import GPSPositionFilter
from src.Modules.DataInterfaceTools.median_filter import MedianFilter
from src.Modules.MessageParsing.fcb_message_parsing import (
    get_fcb_state_from_state_num,
    is_ground_station_message,
)

KEYS_TO_FILTER = [
    Constants.altitude_key,
    Constants.vertical_speed_key,
    Constants.fcb_battery_voltage,
]


class FCBDataInterfaceCore(ThreadedModuleCore):
    """
    Contains common functions to handle parsed data from the fcb

    Used by both the serial ground station interface and the recorded data interface
    """

    def __init__(self):
        super().__init__()
        self.primary_module = True

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
        self.ground_station_position_filter = GPSPositionFilter("Ground Station")
        self.fcb_state_filter = MedianFilter()

        self.filter_dictionary = {}  # Add a filter for each key that we want to filter
        for key in KEYS_TO_FILTER:
            self.filter_dictionary[key] = MedianFilter()

    def spin(self):
        self.connected = False
        self.has_data = False
        self.good_fcb_data = False

        self.updateEveryEnabledLoop()

    def handleParsedData(self, message_type, dictionary, update_on_bad_crc=True):
        # Set the fcb state text
        # This needs to be here so that the fcb state text shows up in the diagnostics box
        if Constants.fcb_state_number_key in dictionary:
            dictionary[Constants.fcb_state_key] = get_fcb_state_from_state_num(dictionary[Constants.fcb_state_number_key])

        self.diagnostics_box_helper.updatePanel(message_type, dictionary)  # Update the diagnostics box with the unfiltered data

        if Constants.crc_key in dictionary:
            self.good_radio_crc = str(dictionary[Constants.crc_key]).lower() == "good"

        # Most of this data only updates if we have a good crc
        if self.good_radio_crc or update_on_bad_crc:
            # Special parse operations to deal with filtering lat and lon data
            if Constants.latitude_key in dictionary and Constants.longitude_key in dictionary:  # If dictionary contains vehicle gps position, filter it
                self.vehicle_position_filter.new_gps_coords(
                    dictionary[Constants.latitude_key],
                    dictionary[Constants.longitude_key],
                )
                [
                    new_lat,
                    new_lon,
                ] = self.vehicle_position_filter.get_filtered_position_output()
                dictionary[Constants.latitude_key] = new_lat
                dictionary[Constants.longitude_key] = new_lon

                if Constants.ground_speed_key not in dictionary:
                    dictionary[Constants.ground_speed_key] = self.vehicle_position_filter.get_filtered_speed_output()

            # Filter ground station lat and lon
            if Constants.ground_station_latitude_key in dictionary and Constants.ground_station_longitude_key in dictionary:
                self.ground_station_position_filter.new_gps_coords(
                    dictionary[Constants.ground_station_latitude_key],
                    dictionary[Constants.ground_station_longitude_key],
                )
                [
                    new_lat,
                    new_lon,
                ] = self.ground_station_position_filter.get_filtered_position_output()
                dictionary[Constants.ground_station_latitude_key] = new_lat
                dictionary[Constants.ground_station_longitude_key] = new_lon

            # Loop through the dictionary of median filters, and filter each data point if it exists
            for key_to_filter in self.filter_dictionary:
                if key_to_filter in dictionary:
                    filter_object = self.filter_dictionary[key_to_filter]
                    filter_object.new_data(dictionary[key_to_filter])
                    dictionary[key_to_filter] = filter_object.get_filtered_data_output()

            # Filter the FCB state, and update the FCB state text
            if Constants.fcb_state_number_key in dictionary:
                self.fcb_state_filter.new_data(dictionary[Constants.fcb_state_number_key])
                dictionary[Constants.fcb_state_number_key] = int(self.fcb_state_filter.get_filtered_data_output())
                dictionary[Constants.fcb_state_key] = get_fcb_state_from_state_num(dictionary[Constants.fcb_state_number_key])

            # We want a rssi value without the "db" text at the end for plotting
            if Constants.rssi_key in dictionary:
                rssi_val = str(dictionary[Constants.rssi_key])
                if " db" in rssi_val:
                    rssi_val = rssi_val.strip(" db")
                    try:
                        dictionary[Constants.rssi_val_key] = float(rssi_val)
                    except:
                        pass

            self.data_dictionary.update(dictionary)

            if not is_ground_station_message(message_type):
                self.last_good_data_time = time.time()
                self.good_fcb_data = True

    def updateEveryEnabledLoop(self):
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

        self.data_dictionary[Constants.primary_annunciator] = self.annunciator.getList()

        self.data_dictionary[Constants.status_source] = self.annunciator.getOverallStatus()
        self.data_dictionary[Constants.raw_message_data_key] = self.diagnostics_box_helper.get_diagnostics_dict()

        self.data_dictionary[Constants.message_age_key] = round(time.time() - self.last_good_data_time, 3)
        self.data_dictionary[Constants.message_time_key] = time.time()
