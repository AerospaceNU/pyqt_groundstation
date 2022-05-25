import time

from src.constants import Constants
from src.Modules.fcb_data_interface_core import FCBDataInterfaceCore
from src.Postprocessing.recorded_data_reader import RecordedDataReader


class GroundStationRecordedDataInterface(FCBDataInterfaceCore):
    """
    Reads recorded data from groundstation back into ground station
    """

    def __init__(self):
        super().__init__()

    def startUp(self):
        self.reader = RecordedDataReader(load_slower=True, logging_callback=lambda data, level=1: self.logToConsole(data, level, override_disabled_check=True))
        self.logToConsole("Done indexing recorded data", 1, override_disabled_check=True)

    def runOnEnableAndDisable(self):
        self.reader.setPacketIndex(0)

        if not self.reader.parsedToFullHistory():
            self.reader.parseIntoIndividualLists()

        # Only use runs where we got packets with the rssi field (meaning that data came in over the radio)
        runs_to_use = []
        if self.enabled:
            for run in self.reader.getRuns():
                [data_series, _] = self.reader.getFullHistoryForKey(run, Constants.rssi_key)
                if len(data_series) > 0 and run not in runs_to_use:
                    runs_to_use.append(run)

        # Put this data in the right spot so we can view it later
        if self.enabled:
            for run in runs_to_use:
                if run not in self.recorded_data_dictionary:
                    self.recorded_data_dictionary[run] = {}

                for key in self.reader.getRecordedDataKeys(run):
                    [data_series, time_series] = self.reader.getFullHistoryForKey(run, key)
                    self.recorded_data_dictionary[run][key] = [data_series, time_series]

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
        self.updateEveryEnabledLoop()
        time.sleep(0.05)
