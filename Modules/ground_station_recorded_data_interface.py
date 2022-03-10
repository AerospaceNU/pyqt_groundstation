import time

from Modules.fcb_data_interface_core import FCBDataInterfaceCore

from Postprocessing.recorded_data_reader import RecordedDataReader

from constants import Constants


class GroundStationRecordedDataInterface(FCBDataInterfaceCore):
    """
    Reads recorded data from groundstation back into ground station
    """

    def __init__(self):
        super().__init__()

        self.reader = RecordedDataReader()

    def runOnEnableAndDisable(self):
        self.reader.setPacketIndex(0)

        if not self.reader.parsedToFullHistory():
            self.reader.parseIntoIndividualLists()

        if self.enabled:
            for key in self.reader.getRecordedDataKeys():
                [data_series, time_series] = self.reader.getFullHistoryForKey(key)
                self.recorded_data_dictionary[key] = [data_series, time_series]

    def spin(self):
        self.good_fcb_data = True
        self.connected = True
        self.has_data = True

        [packet_type, parsed_packet] = self.reader.getNextPacket()
        self.logToConsole("New [{0}] message".format(packet_type), 0)

        # We changed how crc is logged at some point, so this is needed to look at old data
        if Constants.crc_key in parsed_packet and parsed_packet[Constants.crc_key] == "1":
            parsed_packet[Constants.crc_key] = "Good"

        self.handleParsedData(packet_type, parsed_packet)
        self.updateEveryLoop()
        time.sleep(.05)
