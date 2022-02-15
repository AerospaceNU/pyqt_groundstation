"""
turns parsed_message.txt into a .csv file
"""

import csv
import navpy

from constants import Constants
from data_helpers import vector_length

if __name__ == '__main__':
    file = open("../parsed_messages.txt")
    data = file.readlines()

    data_struct = []
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

            data_struct.append(packet_data)

    fields = list(packet_data.keys())

    with open("export.csv", 'w') as csvfile:
        # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        # writing headers (field names)
        writer.writeheader()

        # writing data rows
        writer.writerows(data_struct)
