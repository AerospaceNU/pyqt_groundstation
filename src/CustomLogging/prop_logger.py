import json
import time


class PropLogger:
    def __init__(self, subdir) -> None:
        self.file_idx = 0
        self.subdir = subdir
        self.file_opened = False

        self.csv_file_handle = None

        self.last_columns = ""

    def open_file(self):
        if not self.file_opened:
            other_filename = self.subdir + "/PROP_OTHER_MSGS.txt"
            self.other_writer = open(other_filename, "a")
            self.other_writer.write("RUN START\n")
            self.other_writer.flush()

            self.file_opened = True

    def get_columns(self, msg_json):
        csv_fields = ["timeStamp", "currentState", "engineSequence", "teensyCount", "adcboardCount", "lastTeensyTime", "lastAdcboardTime"]

        sensor_types = ["loadCellSensors", "pressureSensors", "tempSensors", "valves"]

        sensor_values = [msg_json[v] for v in csv_fields if v in msg_json]

        for type_ in sensor_types:
            for sensor in msg_json["data"][type_]:
                csv_fields.append(sensor)
                for key in ["sensorReading", "valveState"]:
                    if key in msg_json["data"][type_][sensor]:
                        sensor_values.append(str(msg_json["data"][type_][sensor][key]))

        return (csv_fields, sensor_values)

    # take in json data and write it to the csv
    # param msg_json is the dictionary of the json provided by the ecs
    def handle_data(self, msg_json):
        csv_fields, sensor_values = self.get_columns(msg_json)

        # If the header changed, best we can do is open a new file
        # Files are cheap
        if csv_fields != self.last_columns:
            self.last_columns = csv_fields
            save_path = self.subdir + f"/PROP_DATA_{self.file_idx}.txt"
            self.file_idx = self.file_idx + 1
            if self.csv_file_handle is not None:
                self.csv_file_handle.close()
            self.csv_file_handle = open(save_path, "w")
            # Write header
            self.csv_file_handle.write(",".join(csv_fields))
            self.csv_file_handle.write("\n")

        self.csv_file_handle.write(",".join(map(lambda it: str(it), sensor_values)))
        self.csv_file_handle.write("\n")

    # handle non-data (error messages, etc) and write to the text file#
    # param msg_json is the dictionary of the json provided by the ecs
    # param other_file is the writer containing
    def handle_other(self, msg_json):
        self.open_file()

        self.other_writer.write("NON-DATA : " + str(round(time.time())) + " : " + json.dumps(msg_json) + "\n")
        self.other_writer.flush()

    # listens for json data from the ecs, calls other methods to parse and write data received
    def log_ws_msg(self, output_json):
        try:
            if output_json["command"] == "DATA":
                self.handle_data(output_json)
            else:
                self.handle_other(output_json)
        except Exception as e:
            self.open_file()

            print("Data logging error:", e, "at time:", str(round(time.time())))
            self.other_writer.write("ERROR at time" + str(round(time.time())) + "\n")
            self.other_writer.write(str(e))
            self.other_writer.write("\n")
