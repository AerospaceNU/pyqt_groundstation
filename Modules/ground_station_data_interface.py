import struct
import time
import serial
import serial.tools.list_ports

from Modules.MessageParsing import fcb_message_parsing
from Modules.MessageParsing.fcb_message_generation import createRadioBandCommandMessage, createCLICommandMessage
from Modules.fcb_data_interface_core import FCBDataInterfaceCore
from Modules.DataInterfaceTools.reconfigure_helper import ReconfigurePage
from Modules.DataInterfaceTools.comms_console_helper import CommsConsoleHelper

from dpf_ground_station import DPFGUI
from constants import Constants

RADIO_433 = 0
RADIO_915 = 1
RADIO_NAMES = {0: "433 MHz", 1: "915 MHz"}


class GroundStationDataInterface(FCBDataInterfaceCore):
    """
    Reads data from the ground station hardware, and parses it
    """

    def __init__(self):
        super().__init__()

        self.nextCheckTime = time.time()
        self.serial_port = "/dev/ttyACM0"
        self.baud_rate = 9600
        self.active_radio = RADIO_433

        self.active_radio_bands = {}
        for radio_id in RADIO_NAMES:
            self.active_radio_bands[radio_id] = 0

        self.outgoing_serial_queue = []

        self.raw_data_file = open("raw_data.txt", "a+")
        self.parsed_messages_file = open("parsed_messages.txt", "a+")
        self.raw_data_file.write("\n\nRUN START {}\n\n".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        self.parsed_messages_file.write("\n\nRUN START {}\n\n".format(time.strftime("%Y-%m-%d %H:%M:%S")))

        self.callbacks_to_add.append(["set_serial_port", self.changeActiveSerialPort])
        self.callbacks_to_add.append([Constants.cli_interface_key, self.cliCommand])

        self.radio_reconfigure_page = ReconfigurePage("Serial Ground Station Config")
        self.radio_reconfigure_page.addEnumOption("radio_types", "433 MHz", RADIO_433)
        self.radio_reconfigure_page.addEnumOption("radio_types", "915 MHz", RADIO_915)
        self.radio_reconfigure_page.updateLine("Target Radio", "enum", "", "Which radio to use", "radio_types")
        self.radio_reconfigure_page.updateLine("Radio Band", "int", description="Which radio band to use")
        self.radio_reconfigure_page.bindCallback("Target Radio", self.onRadioSwitch)
        self.radio_reconfigure_page.bindCallback("Radio Band", self.onBandSwitch)
        radio_reconfigure_callbacks = self.radio_reconfigure_page.getCallbackFunctions(Constants.primary_reconfigure)
        for callback in radio_reconfigure_callbacks:
            self.callbacks_to_add.append([callback, radio_reconfigure_callbacks[callback]])

        self.cliConsole = CommsConsoleHelper()

    def changeActiveSerialPort(self, portName):
        self.serial_port = portName
        self.connected = False

    def cliCommand(self, data):
        self.cliConsole.addEntry(data)
        self.outgoing_serial_queue.append(createCLICommandMessage(self.active_radio, data))

    def onBandSwitch(self, data):
        try:
            data = int(data)
            self.outgoing_serial_queue.append(createRadioBandCommandMessage(0xff, self.active_radio, data))
            self.logToConsole("Switching to band {}".format(data), 1, True)
            self.active_radio_bands[self.active_radio] = data
            self.radio_reconfigure_page.updateLine("Radio Band", "int", data)
        except Exception as e:
            self.logToConsole("Could not switch to band {0}: {1}".format(data, e), 1, True)
            print(e)

    def onRadioSwitch(self, data):
        try:
            data = int(data)
        except:
            pass

        if data in RADIO_NAMES:
            self.active_radio = data
            self.logToConsole("Switching to {} radio".format(RADIO_NAMES[data]), 1, True)
            self.radio_reconfigure_page.updateLine("Radio Band", "int", int(self.active_radio_bands[data]))
        else:
            self.logToConsole("Unknown radio id {}".format(data), 1)

    def spin(self):
        if self.nextCheckTime <= time.time():
            self.logToConsole("Trying to connect to ground station on {}".format(self.serial_port), 0)
            try:
                self.serial = serial.Serial(self.serial_port, self.baud_rate, timeout=0.01)  # Set the serial port timeout really small, so we only get one message at a time
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
                self.writeData()
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
        raw_bytes = self.serial.read(1000)  # Read in bytes
        if len(raw_bytes) == 0:  # If it didn't send a message, we don't parse
            return

        self.raw_data_file.write("{0}: {1}\n".format(time.strftime("%H:%M:%S"), str(raw_bytes)))

        self.last_data_time = time.time()

        try:
            [success, dictionary, message_type, crc] = fcb_message_parsing.parse_fcb_message(raw_bytes)

            if Constants.radio_id_key in dictionary and dictionary[Constants.radio_id_key] != self.active_radio:  # Data coming in over the wrong radio
                return

            if Constants.cli_string_key in dictionary:
                self.cliConsole.autoAddEntry(dictionary[Constants.cli_string_key], from_remote=True)

            if not success:
                self.logToConsole("Could not parse message: {0}".format(message_type), 1)
                self.good_fcb_data = False
            elif not crc:
                self.logToConsole("Bad CRC for {} message".format(message_type), 1)
                self.logMessageToFile(message_type, dictionary)
                self.handleParsedData(message_type, dictionary, update_on_bad_crc=False)
            else:
                self.logToConsole("New [{0}] message".format(message_type), 0)
                self.logMessageToFile(message_type, dictionary)
                self.handleParsedData(message_type, dictionary)

            if not fcb_message_parsing.is_ground_station_message(message_type):
                self.has_data = True
        except struct.error as e:
            self.logToConsole("Can't parse message (length: {2} bytes):\n{1}".format(raw_bytes, e, len(raw_bytes)), 1)

    def writeData(self):
        if len(self.outgoing_serial_queue) > 0:
            try:
                # print("Writing data to serial port: {}".format(self.outgoing_serial_queue[-1]))
                self.serial.write(self.outgoing_serial_queue.pop())
            except Exception as e:
                print(e)

    def updateEveryLoop(self):
        super(GroundStationDataInterface, self).updateEveryLoop()

        self.reconfigure_options_dictionary[self.radio_reconfigure_page.getPageName()] = self.radio_reconfigure_page.getDataStructure()
        self.data_dictionary[Constants.cli_interface_key] = self.cliConsole.getList()

    def logMessageToFile(self, message_type, parsed_message):
        self.parsed_messages_file.write("{0}: {1} {2}\n".format(time.strftime("%H:%M:%S"), message_type, str(parsed_message)))

    def closeOut(self):
        self.raw_data_file.close()
        self.parsed_messages_file.close()
