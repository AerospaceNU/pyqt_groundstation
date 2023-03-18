import logging
import time
from dataclasses import dataclass
from typing import Dict, List

import pynmea2
import serial
import serial.tools.list_ports

from src.constants import Constants
from src.CustomLogging.dpf_logger import SerialLogger
from src.Modules.data_interface_core import ThreadedModuleCore
from src.Modules.DataInterfaceTools.diagnostics_box_helper import DiagnosticsBoxHelper


@dataclass
class EggPacketDescription:
    trigger: str
    message_name: str
    database_key: str
    data_type: type = None
    multiplier: float = 1
    callback_function: callable = None


EGG_STATES = {
    1: "Waiting for Launch",
    2: "Launch Detected",
    3: "N/A",
    4: "Low velocity Detected",
    5: "Nose-Over",
    6: "Drogue Fired",
    7: "Main Fired",
    8: "Failsafe Triggered",
    9: "Landing Detected",
}


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
        self.serial_logger = SerialLogger(self.__class__.__name__)
        self.primary_module = self.config_saver.get("primary_telemetry_source", "False", str).lower() == "true"  # Can't convert a bool directly to a string for some reason
        self.diagnostics_helper = DiagnosticsBoxHelper()

        self.egg_packet_types: Dict[str:EggPacketDescription] = {}
        self.egg_messages = {}

        # Add new packets here
        self.addEggPacketType(EggPacketDescription("#", "Flight time", Constants.timestamp_ms_key, int))  # I think this is flight time, not run time
        self.addEggPacketType(EggPacketDescription("<", "Altitude", Constants.altitude_key, float, 0.3048))  # Ft to meters
        self.addEggPacketType(EggPacketDescription("(", "Vertical Speed", Constants.vertical_speed_key, float, 0.3048))  # Ft/s to m/s
        self.addEggPacketType(EggPacketDescription("\\", "Acceleration", Constants.acceleration_key, float, 0.3048))  # Ft/s^2 to m/s^2
        self.addEggPacketType(EggPacketDescription("!", "Temperature", Constants.temperature_key, float, 0.1))  # Temperature is *10 in packet
        self.addEggPacketType(EggPacketDescription("?", "Voltage", Constants.battery_voltage_key, float, 0.1))  # Voltage is *10 in packet
        self.addEggPacketType(EggPacketDescription("@", "Egg state", "", callback_function=self.parseEggState))
        self.addEggPacketType(EggPacketDescription("~", "Pyro Message", "", callback_function=self.parseChannelMessage))
        self.addEggPacketType(EggPacketDescription("%", "Apogee", ""))
        self.addEggPacketType(EggPacketDescription("^", "Max Velocity", ""))
        self.addEggPacketType(EggPacketDescription("[", "Max Acceleration", ""))

    def addEggPacketType(self, packet_description: EggPacketDescription):
        self.egg_packet_types[packet_description.trigger] = packet_description

    def changeActiveSerialPort(self, port_name):
        self.serial_port = port_name
        self.connected = False

    def spin(self):
        # TODO: Break serial logic out into base class
        if self.nextCheckTime <= time.time():
            self.logger.info(f"Trying to connect to egg finder on {self.serial_port}")
            try:
                self.serial = serial.Serial(self.serial_port, self.baud_rate, timeout=0.01)  # Set the serial port timeout really small, so we only get one message at a time
                self.connected = True
                self.connectedLoop()
                self.nextCheckTime = time.time() + 1
                self.serial.close()
            except IOError as e:
                self.logger.warning(f"Could not connect to egg finder on port {self.serial_port}: [{e}]")
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
                    self.logToConsoleThrottle(f"Egg finder on port {self.serial_port} timed out", logging.ERROR, 1)
                    self.has_data = False
                time.sleep(0.01)
            self.logger.error(f"Disconnected from egg finder on port {self.serial_port}")
        except IOError:
            self.logger.error(f"Lost connection to egg finder on port {self.serial_port}")
            self.connected = False

    def readData(self):
        raw_bytes = self.serial.read(1000)  # Read in bytes
        if len(raw_bytes) == 0:  # If it didn't send a message, we don't parse
            return

        self.last_data_time = time.time()

        try:
            data_string = raw_bytes.decode()
            self.data_buffer += data_string

            self.data_buffer = self.data_buffer.replace(">", "\n")  # Make all packets end with the same character
            split_data = self.data_buffer.split("\n")  # Split on ends of packets

            if len(split_data) > 1:
                self.data_buffer = split_data[-1]
                self.parsePackets(split_data[0:-1])
        except Exception as e:
            self.logger.warn(f"Could not decode egg finder string: {e}")
            return

    def parsePackets(self, packets: List[str]):
        packets = [packet.strip() for packet in packets]

        STUPID_PACKETS = ["@@", "{  }"]  # For some reason we get these random, meaningless packets

        for packet in packets:
            self.serial_logger.write_raw(packet)

            if len(packet) == 0:
                pass
            elif packet in STUPID_PACKETS:
                pass
            elif packet[0] == "$":
                self.parseNMEAString(packet)
            elif packet[0] in self.egg_packet_types.keys():
                self.parseEggPacket(packet)
            else:
                self.logger.warning(f"Unknown packet: [{packet}]")

    def parseEggPacket(self, packet):
        self.logger.info(f"Egg Telemetry packet: {packet}")

        if packet[-1] == ">":  # Shouldn't ever happen now
            packet = packet[0:-1]

        packet_type = str(packet[0])
        if packet_type not in self.egg_packet_types.keys():
            return

        packet_description = self.egg_packet_types[packet_type]
        packet_data = packet[1:]

        if packet_description.callback_function is not None:
            try:
                packet_description.callback_function(packet_data)
            except Exception as e:
                self.logger.warning(f"Unable to call callback function for egg packet type {packet_type}: {e}")

            # Log "parsed" data
            self.serial_logger.write_parsed(self.egg_packet_types[packet_type].message_name, packet_data)
            return
        elif packet_description.data_type == float:
            packet_value = float(packet_data) * packet_description.multiplier
        else:
            packet_value = str(packet_data)

        if self.primary_module and packet_description.database_key != "":  # Put it into database dictionary if we're the primary telemetry source
            self.data_dictionary[packet_description.database_key] = packet_value

        # Keep the last egg message of each type for the text panel
        self.egg_messages[self.egg_packet_types[packet_type].message_name] = packet_value

        # Log the parsed serial message
        self.serial_logger.write_parsed(self.egg_packet_types[packet_type].message_name, packet_value)

    def parseNMEAString(self, nmea_string):
        try:
            if nmea_string.strip() != "":
                msg = pynmea2.parse(nmea_string.strip())

                # TODO add more messages than just GGA
                if type(msg) == pynmea2.types.talker.GGA:
                    self.logger.info(f"Egg finder NMEA GGA: {msg}")
                    self.serial_logger.write_parsed("GPS Position Fix", f"{{latitude: {msg.latitude}, longitude: {msg.longitude}, altitude: {msg.altitude}}}")
                    self.last_good_data_time = time.time()

                    if self.primary_module:
                        self.data_dictionary[Constants.latitude_key] = msg.latitude
                        self.data_dictionary[Constants.longitude_key] = msg.longitude
                        self.data_dictionary[Constants.gps_alt_key] = msg.altitude
                    else:
                        self.data_dictionary[Constants.backup_gps_latitude] = msg.latitude
                        self.data_dictionary[Constants.backup_gps_longitude] = msg.longitude
                        self.data_dictionary[Constants.backup_gps_altitude] = msg.altitude

                    self.egg_messages["Latitude"] = msg.latitude
                    self.egg_messages["Longitude"] = msg.longitude
                    self.egg_messages["GPS altitude"] = msg.altitude
        except Exception as e:
            self.logger.error(f"Could not parse eggfinder NMEA string {nmea_string}: {e}")

    def parseEggState(self, packet_data):
        state_num = int(packet_data)

        if state_num in EGG_STATES:
            self.data_dictionary[Constants.fcb_state_number_key] = state_num
            self.data_dictionary[Constants.fcb_state_key] = EGG_STATES[state_num]

            self.egg_messages["Egg state"] = EGG_STATES[state_num]
        else:
            self.logger.warning(f"Invalid EGG state: {state_num}")

    def parseChannelMessage(self, packet_data: str):
        num_pyros = len(packet_data)

        pyro_continuity = [False] * num_pyros
        pyro_fired = [False] * num_pyros

        for i in range(len(packet_data)):
            pyro = packet_data[i]

            if pyro == "-":
                pass
            elif pyro.isnumeric():
                pyro_fired[i] = True
            else:
                pyro_continuity[i] = True

        self.data_dictionary[Constants.pyro_continuity] = pyro_continuity
        self.data_dictionary[Constants.pyro_fire_status] = pyro_fired

        self.egg_messages["Pyro Continuity"] = pyro_continuity
        self.egg_messages["Pyro Fired"] = pyro_fired

    def updateEveryLoop(self):
        if self.primary_module:
            self.diagnostics_helper.updatePanel("Egg Finder Data", self.egg_messages)
            self.data_dictionary[Constants.raw_message_data_key] = self.diagnostics_helper.get_diagnostics_dict()

        self.data_dictionary[Constants.egg_finder_age] = round(time.time() - self.last_good_data_time, 3)
