"""
Reads recorded data from groundstation back into ground station
"""

import time

from DataInterfaces.fcb_data_interface_core import FCBDataInterfaceCore

from Postprocessing.recorded_data_reader import RecordedDataReader


class GroundStationRecordedDataInterface(FCBDataInterfaceCore):
    def __init__(self):
        super().__init__()

        self.reader = RecordedDataReader()

    def spin(self):
        self.good_fcb_data = True
        self.connected = True
        self.has_data = True

        [packet_type, parsed_packet] = self.reader.getNextPacket()
        self.logToConsole("New [{0}] message".format(packet_type), 0)

        self.handleParsedData(packet_type, parsed_packet)
        self.updateEveryLoop()
        time.sleep(.05)
