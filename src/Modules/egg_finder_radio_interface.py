import time

import pynmea2
import serial
import serial.tools.list_ports

from src.constants import Constants
from src.Modules.data_interface_core import ThreadedModuleCore


class EggFinderRadioInterface(ThreadedModuleCore):
    """
    Gets data from egg finder radio
    """

    def __init__(self):
        super().__init__()

        self.nextCheckTime = time.time()
        self.serial_port = ""
        self.baud_rate = 9600
        self.last_data_time = time.time()

        self.connected = False
        self.has_data = False

        self.data_buffer = ""

        self.last_good_data_time = 0

        self.serial_devices["Egg Finder"] = self.changeActiveSerialPort

    def changeActiveSerialPort(self, portName):
        self.serial_port = portName
        self.connected = False

    def spin(self):
        # TODO: Break serial logic out into base class
        if self.nextCheckTime <= time.time():
            self.logToConsole("Trying to connect to egg finder on {}".format(self.serial_port), 0)
            try:
                self.serial = serial.Serial(self.serial_port, self.baud_rate, timeout=0.01)  # Set the serial port timeout really small, so we only get one message at a time
                self.connected = True
                self.connectedLoop()
                self.nextCheckTime = time.time() + 1
                self.serial.close()
            except IOError as e:
                self.logToConsole("Could not connect to egg finder on port {}".format(self.serial_port), 2)
                # print(e)
                self.nextCheckTime = time.time() + 5

        self.connected = False
        self.has_data = False

        self.updateEveryLoop()

    def connectedLoop(self):
        self.last_data_time = time.time()
        try:
            while self.connected and self.should_be_running and self.enabled:
                self.readData()
                self.updateEveryLoop()
                if time.time() - self.last_data_time > 5:  # Timeout checks on any data, not just good data
                    self.logToConsoleAndCheck("Egg finder on port {} timed out".format(self.serial_port), 2)
                    self.has_data = False
                time.sleep(0.01)
            self.logToConsole("Disconnected from egg finder on port {}".format(self.serial_port), 2)
        except IOError:
            self.logToConsole("Lost connection to egg finder on port {}".format(self.serial_port), 2)
            self.connected = False

    def readData(self):
        raw_bytes = self.serial.read(1000)  # Read in bytes
        if len(raw_bytes) == 0:  # If it didn't send a message, we don't parse
            return

        self.last_data_time = time.time()

        try:
            data_string = raw_bytes.decode()
            self.data_buffer += data_string

            if "\n" in self.data_buffer:
                nmea_strings = self.data_buffer.split("\n")[0:-1]
                self.data_buffer = self.data_buffer.split("\n")[-1]
            else:
                nmea_strings = []
        except Exception as e:
            print("Could not decode egg finder string: {0}".format(e))
            return

        try:
            for nmea_string in nmea_strings:
                if nmea_string.strip() != "":
                    msg = pynmea2.parse(nmea_string.strip())

                    if type(msg) == pynmea2.types.talker.GGA:
                        self.logToConsole("Egg finder : {1}".format(time.time(), msg), 0)

                        self.data_dictionary[Constants.egg_finder_latitude] = msg.latitude
                        self.data_dictionary[Constants.egg_finder_longitude] = msg.longitude
                        self.data_dictionary[Constants.egg_finder_altitude] = msg.altitude
                        self.last_good_data_time = time.time()

        except Exception as e:
            pass
            # print("Could not parse NMEA string: {0}".format(e))

    def updateEveryLoop(self):
        self.data_dictionary[Constants.egg_finder_age] = round(time.time() - self.last_good_data_time, 3)
