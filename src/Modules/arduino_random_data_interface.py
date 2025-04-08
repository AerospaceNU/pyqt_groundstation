import serial
import time

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.constants import Constants
from src.Modules.module_core import ThreadedModuleCore

class ArduinoDataInterface(ThreadedModuleCore):
    """
    Reads and processes incoming data from an Arduino via serial connection.
    """
    
    def __init__(self, serial_port="/dev/cu.usbmodem101", baud_rate=9600):
        super().__init__()
        self.primary_module = True
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.last_data_time = 0
        self.raw_data = ''
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
            # print(f"Raw data received: {raw_data}")  # Debugging output
            self.raw_data = raw_data.split(";")
            # return self.parse_data(self.raw_data)
            
    def write_arduino_data(self, data):
        print("called write and its writing! datA:", data)
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(f"{data}\n".encode("utf-8"))

    def spin(self):
        """Continuously checks for new data and updates the dictionary."""
        while True:
            self.read_arduino_data()
            if self.raw_data:
                parts = self.raw_data
                payload_landing_site_temp = float(parts[2])
                payload_battery = float(parts[3])
                payload_apogee_altitude = float(parts[4])
                payload_max_velocity = float(parts[6])
                payload_landing_velocity = float(parts[7])
                payload_landing_time = float(parts[1])
                payload_survivabilty = float(parts[9])
                payload_orientation = float(parts[5])
                self.data_dictionary[Constants.payload_landing_site_temperature_key] = payload_landing_site_temp
                self.data_dictionary[Constants.payload_landing_time_key] = payload_landing_time
                self.data_dictionary[Constants.payload_battery_key] = payload_battery / 10
                self.data_dictionary[Constants.payload_apogee_altitude_key] = payload_apogee_altitude
                self.data_dictionary[Constants.payload_max_velocity_key] = payload_max_velocity
                self.data_dictionary[Constants.payload_landing_velocity_key] = payload_landing_velocity
                self.data_dictionary[Constants.payload_crew_survivability_key] = payload_survivabilty
                self.data_dictionary[Constants.payload_orientation_key] = payload_orientation
            time.sleep(.02)  # Adjust polling rate as needed

if __name__ == "__main__":
    arduino_interface = ArduinoDataInterface()
    arduino_interface.spin()
