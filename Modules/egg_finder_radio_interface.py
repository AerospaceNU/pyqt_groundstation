import time
import serial
import serial.tools.list_ports
import pynmea2

from Modules.data_interface_core import ThreadedModuleCore
from Modules.DataInterfaceTools.reconfigure_helper import ReconfigurePage
from Modules.DataInterfaceTools.comms_console_helper import CommsConsoleHelper

from constants import Constants


class EggFinderRadioInterface(ThreadedModuleCore):
    """
    Gets data from egg finder radio
    """

    def __init__(self):
        super().__init__()

        self.nextCheckTime = time.time()
        self.serial_port = "/dev/ttyACM0"
        self.baud_rate = 9600  # 4800?
        self.last_data_time = time.time()

        self.connected = False
        self.has_data = False

        self.callbacks_to_add.append(["set_egg_serial_port", self.changeActiveSerialPort])

        # self.radio_reconfigure_page = ReconfigurePage("Egg finder port config")
        # self.radio_reconfigure_page.addEnumOption("radio_types", "433 MHz", RADIO_433)
        # self.radio_reconfigure_page.addEnumOption("radio_types", "915 MHz", RADIO_915)
        # self.radio_reconfigure_page.updateLine("Target Radio", "enum", "", "Which radio to use", "radio_types")
        # self.radio_reconfigure_page.updateLine("Radio Band", "int", description="Which radio band to use")
        # self.radio_reconfigure_page.bindCallback("Target Radio", self.onRadioSwitch)
        # self.radio_reconfigure_page.bindCallback("Radio Band", self.onBandSwitch)

        # reconfigure_callbacks = self.radio_reconfigure_page.getCallbackFunctions(Constants.primary_reconfigure)
        # for callback in reconfigure_callbacks:
        #     self.callbacks_to_add.append([callback, reconfigure_callbacks[callback]])

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

        data_string = raw_bytes.decode()
        nmea_strings = data_string.split("\n")

        try:
            for nmea_string in nmea_strings:
                if nmea_string.strip() != "":
                    msg = pynmea2.parse(nmea_string.strip())

                    if type(msg) == pynmea2.types.talker.GGA:
                        self.logToConsole("Egg finder : {1}".format(time.time(), msg), 0)

                        self.data_dictionary[Constants.egg_finder_latitude] = msg.latitude
                        self.data_dictionary[Constants.egg_finder_longitude] = msg.longitude
                        self.data_dictionary[Constants.egg_finder_altitude] = msg.altitude

        except Exception as e:
            print(e)

    def updateEveryLoop(self):
        pass
