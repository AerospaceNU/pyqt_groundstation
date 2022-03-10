"""
Class to read recorded data
"""

import time
import navpy
import datetime

from constants import Constants
from data_helpers import vector_length


class RecordedDataReader(object):
    def __init__(self, file_name="parsed_messages.txt", load_slower=False):
        file = open(file_name)
        data = file.readlines()

        self.data_struct = []
        self.packet_types = []
        self.full_history_data_struct = {}  # {run_name: {run_dict}}
        self.parsed_to_full_history = False
        has_first_point = False
        first_point = []

        packet_data = {}
        data_date = datetime.datetime.fromtimestamp(0).date()
        run_number = 0

        for line in data:
            if len(line.strip()) == 0:
                pass
            elif "RUN START" in line:
                timestamp_string = line.split("RUN START")[1].strip()
                data_date = datetime.datetime.fromisoformat(timestamp_string).date()
                run_number += 1
            else:
                try:
                    timestamp = line.split(" ")[0][0:-1]
                    nan = float("NaN")  # Hack to make the eval statement work if nans are saved out
                    packet_type = line.split(timestamp)[1].split("{")[0][2:].strip()  # don't even ask
                    packet_data = eval("{" + line.split("{")[1])

                    timestamp_string = "{0} {1}".format(str(data_date), timestamp)
                    packet_data["timestamp"] = timestamp_string
                    packet_data["run_number"] = run_number
                except Exception as e:
                    print(e)
                    continue

                # Calculate distance from start
                if Constants.latitude_key in packet_data and packet_data[Constants.latitude_key] != 0:
                    if not has_first_point:
                        first_point = [packet_data[Constants.latitude_key], packet_data[Constants.longitude_key]]
                        has_first_point = True

                    ned = navpy.lla2ned(packet_data[Constants.latitude_key], packet_data[Constants.longitude_key], 0, first_point[0], first_point[1], 0)
                    distance = vector_length(ned[0], ned[1])
                    packet_data["distance"] = distance

                self.data_struct.append(packet_data)
                self.packet_types.append(packet_type)

            if load_slower:
                time.sleep(0.000000001)  # This many 0s probably don't help, but this sleep keeps the file indexing from taking all the CPU resources

        self.fields = list(packet_data.keys())
        self.packetIndex = 0

    def parseIntoIndividualLists(self):
        if len(self.data_struct) == 0:
            return
        if "timestamp" not in self.data_struct[0]:
            return

        first_time = datetime.datetime.fromisoformat(self.data_struct[0]["timestamp"])
        run_number = 0

        for packet in self.data_struct:
            if "run_number" in packet:
                run_number = packet["run_number"]

            run_name = "run_{}".format(run_number)
            for key in packet:
                if run_name not in self.full_history_data_struct:
                    self.full_history_data_struct[run_name] = {}
                if key not in self.full_history_data_struct[run_name]:
                    self.full_history_data_struct[run_name][key] = ([], [])

                data_time = datetime.datetime.fromisoformat(packet["timestamp"])
                delta_time = data_time - first_time

                self.full_history_data_struct[run_name][key][0].append(packet[key])
                self.full_history_data_struct[run_name][key][1].append(delta_time.seconds)

        self.parsed_to_full_history = True

    def getRuns(self):
        return list(self.full_history_data_struct.keys())

    def getRecordedDataKeys(self, run):
        if run in self.full_history_data_struct:
            return list(self.full_history_data_struct[run].keys())
        else:
            return []

    def getFullHistoryForKey(self, run, key):
        """
        Returns (data_series, time_series)
        """

        if run not in self.full_history_data_struct:
            return [], []
        if key not in self.full_history_data_struct[run]:
            return [], []
        else:
            return self.full_history_data_struct[run][key]

    def parsedToFullHistory(self):
        return self.parsed_to_full_history

    def getPacket(self, packet_num):
        if packet_num < len(self.packet_types):
            return [self.packet_types[packet_num], self.data_struct[packet_num]]
        else:
            return ["", {}]

    def getNextPacket(self):
        self.packetIndex += 1
        return self.getPacket(self.packetIndex)

    def setPacketIndex(self, packet_index):
        self.packetIndex = packet_index
