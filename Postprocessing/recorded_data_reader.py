"""
Class to read recorded data
"""

import navpy

from constants import Constants
from data_helpers import vector_length


class RecordedDataReader(object):
    def __init__(self, file_name="parsed_messages.txt"):
        file = open(file_name)
        data = file.readlines()

        self.data_struct = []
        self.packet_types = []
        has_first_point = False
        first_point = []

        for line in data:
            if len(line.strip()) == 0 or "RUN START" in line:
                pass
            else:
                timestamp = line.split(" ")[0][0:-1]
                packet_type = line.split(timestamp)[1].split("{")[0][2:].strip()  # don't even ask
                packet_data = eval("{" + line.split("{")[1])
                packet_data["timestamp"] = timestamp

                # Calculate distance from start
                if packet_data[Constants.latitude_key] != 0:
                    if not has_first_point:
                        first_point = [packet_data[Constants.latitude_key], packet_data[Constants.longitude_key]]
                        has_first_point = True

                    ned = navpy.lla2ned(packet_data[Constants.latitude_key], packet_data[Constants.longitude_key], 0, first_point[0], first_point[1], 0)
                    distance = vector_length(ned[0], ned[1])
                    packet_data["distance"] = distance

                self.data_struct.append(packet_data)
                self.packet_types.append(packet_type)

        self.fields = list(packet_data.keys())
        self.packetIndex = 0

    def getPacket(self, packet_num):
        if packet_num < len(self.packet_types):
            return [self.packet_types[packet_num], self.data_struct[packet_num]]
        else:
            return ["", {}]

    def getNextPacket(self):
        self.packetIndex += 1
        return self.getPacket(self.packetIndex)
