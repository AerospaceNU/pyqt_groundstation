import logging
import struct
import time

import serial
import serial.tools.list_ports
from src.CustomLogging.dpf_logger import SerialLogger

from src.constants import Constants
from src.Modules.DataInterfaceTools.comms_console_helper import CommsConsoleHelper
from src.Modules.DataInterfaceTools.reconfigure_helper import ReconfigurePage
from src.Modules.fcb_data_interface_core import FCBDataInterfaceCore
from src.Modules.MessageParsing import fcb_message_parsing
from src.Modules.MessageParsing.fcb_message_generation import (
    createCLICommandMessage,
    createRadioBandCommandMessage,
)

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
        self.serial_port = ""
        self.baud_rate = 9600
        self.active_radio = RADIO_433

        self.active_radio_bands = {}
        for radio_id in RADIO_NAMES:
            self.active_radio_bands[radio_id] = 0

        self.outgoing_serial_queue = []

        self.serial_logger = SerialLogger(self.__class__.__name__)

        self.serial_devices["Ground Station"] = self.changeActiveSerialPort

        self.callbacks_to_add.append([Constants.cli_interface_key, self.cliCommand])

        self.radio_reconfigure_page = ReconfigurePage("Serial Ground Station Config")
        self.radio_reconfigure_page.addEnumOption("radio_types", "433 MHz", RADIO_433)
        self.radio_reconfigure_page.addEnumOption("radio_types", "915 MHz", RADIO_915)
        self.radio_reconfigure_page.updateLine("Target Radio", "enum", "", "Which radio to use", "radio_types")
        self.radio_reconfigure_page.updateLine("Radio Band", "int", description="Which radio band to use")
        self.radio_reconfigure_page.bindCallback("Target Radio", self.onRadioSwitch)
        self.radio_reconfigure_page.bindCallback("Radio Band", self.onBandSwitch)

        reconfigure_callbacks = self.radio_reconfigure_page.getCallbackFunctions(Constants.primary_reconfigure)
        for callback in reconfigure_callbacks:
            self.callbacks_to_add.append([callback, reconfigure_callbacks[callback]])

        self.cliConsole = CommsConsoleHelper()

        self.log_to_file = True

    def changeActiveSerialPort(self, portName):
        self.serial_port = portName
        self.connected = False

    def cliCommand(self, data):
        self.cliConsole.manualAddEntry(data)
        self.outgoing_serial_queue.append(createCLICommandMessage(self.active_radio, data))

    def onBandSwitch(self, data):
        try:
            data = int(data)
            self.outgoing_serial_queue.append(createRadioBandCommandMessage(0xFF, self.active_radio, data))
            self.logger.info("Switching to band {}".format(data))
            self.active_radio_bands[self.active_radio] = data
            self.radio_reconfigure_page.updateLine("Radio Band", "int", data)
        except Exception as e:
            self.logger.error("Could not switch to band {0}: {1}".format(data, e))
            print(e)

    def onRadioSwitch(self, data):
        try:
            data = int(data)
        except ValueError:
            return

        if data in RADIO_NAMES:
            self.active_radio = data
            self.logger.info("Switching to {} radio".format(RADIO_NAMES[data]))
            self.radio_reconfigure_page.updateLine("Radio Band", "int", int(self.active_radio_bands[data]))
        else:
            self.logger.warning("Unknown radio id {}".format(data))

    def spin(self):
        if self.nextCheckTime <= time.time():
            self.logger.info("Trying to connect to ground station on {}".format(self.serial_port))
            try:
                self.serial = serial.Serial(self.serial_port, self.baud_rate, timeout=0.01)  # Set the serial port timeout really small, so we only get one message at a time
                self.connected = True
                self.onRadioSwitch(self.active_radio)
                self.onBandSwitch(0)
                self.connectedLoop()
                self.nextCheckTime = time.time() + 1
                self.serial.close()
            except IOError:
                self.logger.warning("Could not connect to ground station on port {}".format(self.serial_port))
                self.nextCheckTime = time.time() + 5

        self.connected = False
        self.has_data = False
        self.good_fcb_data = False

        self.updateEveryEnabledLoop()

    def connectedLoop(self):
        self.last_data_time = time.time()
        try:
            while self.connected and self.should_be_running and self.enabled:
                self.readData()
                self.writeData()
                self.updateEveryEnabledLoop()
                if time.time() - self.last_data_time > 5:  # Timeout checks on any data, not just good data
                    self.logToConsoleAndCheck(
                        "Ground station on port {} timed out".format(self.serial_port),
                        logging.ERROR,
                    )
                    self.has_data = False
                    self.good_fcb_data = False
                time.sleep(0.01)
            self.logger.info(
                "Disconnected from ground station on port {}".format(self.serial_port),
                logging.ERROR,
            )
        except IOError:
            self.logger.info(
                "Lost connection to ground station on port {}".format(self.serial_port),
                logging.ERROR,
            )
            self.connected = False

    def parseData(self, raw_bytes):
        try:
            [
                success,
                dictionary,
                message_type,
                crc,
            ] = fcb_message_parsing.parse_fcb_message(raw_bytes)

            if Constants.radio_id_key in dictionary and dictionary[Constants.radio_id_key] != self.active_radio:  # Data coming in over the wrong radio
                return

            if Constants.cli_string_key in dictionary:
                self.cliConsole.autoAddEntry(dictionary[Constants.cli_string_key], from_remote=True)

            if not success:
                self.logger.warning("Could not parse message: {0}".format(message_type))
                self.good_fcb_data = False
            elif not crc:
                self.logger.warning("Bad CRC for {} message".format(message_type))
                self.logMessageToFile(message_type, dictionary)
                self.handleParsedData(message_type, dictionary, update_on_bad_crc=False)
            else:
                self.logger.info("New [{0}] message".format(message_type))
                self.logMessageToFile(message_type, dictionary)
                self.handleParsedData(message_type, dictionary)

            if not fcb_message_parsing.is_ground_station_message(message_type):
                self.has_data = True
        except struct.error as e:
            self.logger.warning(
                "Can't parse message (length: {1} bytes):\n{0}".format(e, len(raw_bytes)),
            )

    def readData(self):
        raw_bytes = self.serial.read(fcb_message_parsing.PACKET_LENGTH)  # Read in bytes
        if len(raw_bytes) == 0:  # If it didn't send a message, we don't parse
            return

        # self.parseData(raw_bytes)

        for i in range(0, len(raw_bytes), fcb_message_parsing.PACKET_LENGTH):
            self.parseData(raw_bytes[i : i + fcb_message_parsing.PACKET_LENGTH])
        self.serial.flushInput()

        if self.log_to_file:
            self.serial_logger.write_raw(raw_bytes)

        self.last_data_time = time.time()

    def writeData(self):
        if len(self.outgoing_serial_queue) > 0:
            try:
                # print("Writing data to serial port: {}".format(self.outgoing_serial_queue[0]))
                self.serial.write(self.outgoing_serial_queue.pop(0))
            except Exception as e:
                print(e)

    def updateEveryEnabledLoop(self):
        super(GroundStationDataInterface, self).updateEveryEnabledLoop()

        self.reconfigure_options_dictionary[self.radio_reconfigure_page.getPageName()] = self.radio_reconfigure_page.getDataStructure()
        self.data_dictionary[Constants.cli_interface_key] = self.cliConsole.getList()

    def logMessageToFile(self, message_type, parsed_message):
        if self.log_to_file:
            self.serial_logger.write_parsed(message_type, str(parsed_message))

    def closeOut(self):
        self.serial_logger.close()
