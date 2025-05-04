import os
import sys
import time

import numpy as np
import serial

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.constants import Constants
from src.Modules.module_core import ThreadedModuleCore


class ArduinoDataInterface(ThreadedModuleCore):
    """
    Reads and processes incoming data from an Arduino via serial connection.
    """

    def __init__(self, serial_port="COM6", baud_rate=9600):
        super().__init__()
        self.callback_handler.addCallback("write_arduino", self.write_arduino_data)
        self.primary_module = True
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.last_data_time = 0
        self.raw_data = ""
        self.arduino_log_str = ""

        self.connect_to_arduino()

    def connect_to_arduino(self):
        """Establishes a connection to the Arduino."""
        try:
            self.serial_conn = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            print(f"Connected to Arduino on {self.serial_port}")  # Debugging output
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")  # Debugging output
            self.serial_conn = None

    def read_arduino_data(self):
        """Reads a line of data from the Arduino and parses it."""
        if self.serial_conn and self.serial_conn.in_waiting > 0:
            raw_data = self.serial_conn.readline().decode("utf-8").strip()
            self.last_data_time = time.time()
            self.arduino_log_str += raw_data + "\n"
            self.data_dictionary["payload_logs"] = self.arduino_log_str
            self.raw_data = raw_data.split(";")

    def write_arduino_data(self, data):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(f"{data}\n".encode("utf-8"))

    def spin(self):
        """Continuously checks for new data and updates the dictionary."""
        while True:
            self.read_arduino_data()
            if len(self.raw_data) == 12:
                parts = self.raw_data
                payload_run_time = int(parts[1])
                payload_landing_time = int(parts[2])
                payload_landing_site_temp = int(parts[3])
                payload_battery = int(parts[4])
                payload_apogee_altitude = int(parts[5])
                payload_orientation = int(parts[6])
                payload_max_velocity = int(parts[7])
                payload_landing_velocity = int(parts[8])
                payload_acceleration = int(parts[9])
                payload_survivabilty = int(parts[10])

                self.data_dictionary[Constants.payload_run_time_key] = payload_run_time
                self.data_dictionary[Constants.payload_landing_time_key] = payload_landing_time
                self.data_dictionary[Constants.payload_landing_site_temperature_key] = round(payload_landing_site_temp - 273.15, 2)
                self.data_dictionary[Constants.payload_battery_key] = payload_battery / 10
                self.data_dictionary[Constants.payload_apogee_altitude_key] = payload_apogee_altitude
                self.data_dictionary[Constants.payload_orientation_key] = payload_orientation
                self.data_dictionary[Constants.payload_max_velocity_key] = payload_max_velocity
                self.data_dictionary[Constants.payload_landing_velocity_key] = payload_landing_velocity
                self.data_dictionary[Constants.payload_acceleration_key] = payload_acceleration
                self.data_dictionary[Constants.payload_crew_survivability_key] = payload_survivabilty

            time.sleep(0.02)  # Adjust polling rate as needed
