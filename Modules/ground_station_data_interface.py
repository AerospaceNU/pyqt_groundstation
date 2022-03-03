"""
Reads data from the ground station hardware, and parses it
"""

import struct
import time
import serial
import serial.tools.list_ports

from Modules.MessageParsing import fcb_message_parsing
from Modules.fcb_data_interface_core import FCBDataInterfaceCore

from dpf_ground_station import DPFGUI


class GroundStationDataInterface(FCBDataInterfaceCore):
    def __init__(self, gui: DPFGUI):
        super().__init__()

        self.gui_object = gui  # I'm not really sure if this is a good idea or not, but I need the functionality

        self.nextCheckTime = time.time()
        self.serial_port = "/dev/ttyACM0"
        self.baud_rate = 9600

        self.raw_data_file = open("raw_data.txt", "a+")
        self.parsed_messages_file = open("parsed_messages.txt", "a+")

        self.raw_data_file.write("\n\nRUN START {}\n\n".format(time.strftime("%Y-%M-%d %H:%M:%S")))
        self.parsed_messages_file.write("\n\nRUN START {}\n\n".format(time.strftime("%Y-%M-%d %H:%M:%S")))

        self.gui_object.addCallback("set_serial_port", self.changeActiveSerialPort)

    def changeActiveSerialPort(self, portName):
        self.serial_port = portName
        self.connected = False

    def spin(self):
        if self.nextCheckTime <= time.time():
            self.logToConsole("Trying to connect to ground station on {}".format(self.serial_port), 0)
            try:
                self.serial = serial.Serial(self.serial_port, self.baud_rate, timeout=0.05)  # Set the serial port timeout really small, so we only get one message at a time
                self.connected = True
                self.connectedLoop()
                self.nextCheckTime = time.time() + 1
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
        self.last_data_time = time.time()
        try:
            while self.connected and self.should_be_running and self.enabled:
                self.readData()
                time.sleep(0.01)
                if time.time() - self.last_data_time > 5:  # Timeout checks on any data, not just good data
                    self.logToConsoleAndCheck("Ground station on port {} timed out".format(self.serial_port), 2)
                    self.has_data = False
                    self.good_fcb_data = False
                self.updateEveryLoop()
            self.logToConsole("Disconnected from ground station on port {}".format(self.serial_port), 2)
        except IOError:
            self.logToConsole("Lost connection to ground station on port {}".format(self.serial_port), 2)
            self.connected = False

    def readData(self):
        raw_bytes = self.serial.read(50)  # Read in bytes
        if len(raw_bytes) == 0:  # If it didn't send a message, we don't parse
            return

        self.raw_data_file.write("{0}: {1}\n".format(time.strftime("%H:%M:%S"), str(raw_bytes)))

        self.last_data_time = time.time()

        try:
            [success, dictionary, message_type, crc] = fcb_message_parsing.parse_fcb_message(raw_bytes)

            if not success:
                self.logToConsole("Could not parse message: {0}".format(message_type), 1)
                self.good_fcb_data = False
            elif not crc:
                self.logToConsole("Bad CRC for {} message".format(message_type), 1)
                self.logMessageToFile(message_type, dictionary)
                self.handleParsedData(message_type, dictionary)
            else:
                self.logToConsole("New [{0}] message".format(message_type), 0)
                self.logMessageToFile(message_type, dictionary)
                self.handleParsedData(message_type, dictionary)

            if not fcb_message_parsing.is_ground_station_message(message_type):
                self.has_data = True
        except struct.error as e:
            self.logToConsole("Can't parse message (length: {2} bytes):\n{1}".format(raw_bytes, e, len(raw_bytes)), 1)

    def logMessageToFile(self, message_type, parsed_message):
        self.parsed_messages_file.write("{0}: {1} {2}\n".format(time.strftime("%H:%M:%S"), message_type, str(parsed_message)))
