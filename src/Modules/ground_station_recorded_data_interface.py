import os
import time

from src.constants import Constants
from src.Modules.fcb_data_interface_core import FCBDataInterfaceCore
from src.Postprocessing.recorded_data_reader import RecordedDataReader


class GroundStationRecordedDataInterface(FCBDataInterfaceCore):
    """
    Reads recorded data from groundstation back into ground station by calling into fcb_data_interface_core

    TODO: each log file can only ever have one run, we should refactor this to reflect that
    """

    def __init__(self):
        super().__init__()

        self.file_name = ""
        self.reader = None

    def startUp(self):
        pass

    def runOnEnableAndDisable(self):
        if self.enabled and len(self.file_name) > 0:
            self.reader = RecordedDataReader(load_slower=True, logging_callback=self.logger.info, file_name=self.file_name)
            self.logger.info("Done indexing recorded data")

            if not self.reader.parsedToFullHistory():
                self.reader.parseIntoIndividualLists()

            # Only use runs where we got packets with the rssi field (meaning that data came in over the radio)
            runs_to_use = []
            for run in self.reader.getRuns():
                [data_series, _] = self.reader.getFullHistoryForKey(run, Constants.rssi_key)
                if len(data_series) > 0 and run not in runs_to_use:
                    runs_to_use.append(run)

            # Put this data in the right spot so we can view it later
            for run in runs_to_use:
                if run not in self.recorded_data_dictionary:
                    self.recorded_data_dictionary[run] = {}

                for key in self.reader.getRecordedDataKeys(run):
                    [data_series, time_series] = self.reader.getFullHistoryForKey(run, key)
                    self.recorded_data_dictionary[run][key] = [data_series, time_series]

    def hasRecordedData(self):
        """
        Tell the upstream GUI we always have recorded data to provide
        """
        return True

    def getRunNames(self):
        """
        Runs every tick of the GUI (which seems unnecessarily fast)
        """
        runs = list(filter(lambda it: os.path.isdir(f"logs/{it}") and os.path.exists(f"logs/{it}/GroundStationDataInterface_parsed.txt"), os.listdir("logs")))
        runs.sort(reverse=True)
        return runs

    def setSpecificRunSelected(self, run_name):
        pass

    def getSpecificRun(self, run_name):
        self.file_name = f"logs/{run_name}/GroundStationDataInterface_parsed.txt"
        # re-trigger indexing if required
        self.runOnEnableAndDisable()

        return super().getSpecificRun(run_name)

    def spin(self):
        if self.reader is None:
            self.good_fcb_data = False
            self.connected = False
            self.has_data = False
            return

        self.good_fcb_data = True
        self.connected = True
        self.has_data = True

        [packet_type, parsed_packet] = self.reader.getNextPacket()
        self.logger.info("New [{0}] message".format(packet_type))

        # We changed how crc is logged at some point, so this is needed to look at old data
        if Constants.crc_key in parsed_packet and parsed_packet[Constants.crc_key] == "1":
            parsed_packet[Constants.crc_key] = "Good"

        self.handleParsedData(packet_type, parsed_packet)
        self.updateEveryEnabledLoop()
        time.sleep(0.05)
