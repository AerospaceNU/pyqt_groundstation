"""
turns parsed_message.txt into a .csv file
"""

import csv

from Postprocessing.recorded_data_reader import RecordedDataReader

if __name__ == '__main__':
    reader = RecordedDataReader(file_name="../parsed_messages.txt")

    with open("export.csv", 'w') as csvfile:
        # creating a csv dict writer object
        writer = csv.DictWriter(csvfile, fieldnames=reader.fields)

        # writing headers (field names)
        writer.writeheader()

        # writing data rows
        writer.writerows(reader.data_struct)
