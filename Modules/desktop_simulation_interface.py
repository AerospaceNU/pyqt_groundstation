
import struct
import sys
import socket
from Modules.ground_station_data_interface import GroundStationDataInterface
from constants import Constants
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server


class LocalSimulationFlightInterface(GroundStationDataInterface):
    """
    Generates random data for testing
    """

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

        super().__init__()

    def recv_size(self):
        the_socket = self.socket

        # 4 bytes appended to 128
        ret = the_socket.recv(132)

        return ret

    def runOnEnableAndDisable(self):
        if self.enabled:
            pass

    def spin(self):
        self.good_fcb_data = True
        self.connected = True
        # self.active_radio = 1
        self.has_data = True

        data = self.recv_size()
        self.parseData(data)

        # [packet_type, parsed_packet] = self.reader.getNextPacket()

        # self.logToConsole("New [{0}] message".format(packet_type), 0)

        # # We changed how crc is logged at some point, so this is needed to look at old data
        # if Constants.crc_key in parsed_packet and parsed_packet[Constants.crc_key] == "1":
        #     parsed_packet[Constants.crc_key] = "Good"

        # self.handleParsedData(packet_type, parsed_packet)
        self.updateEveryLoop()
