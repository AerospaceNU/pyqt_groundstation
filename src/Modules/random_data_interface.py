import math
import random
import time

import navpy

from src.constants import Constants
from src.Modules.data_interface_core import ThreadedModuleCore
from src.Modules.DataInterfaceTools.gps_position_filter import GPSPositionFilter


class RandomDataInterface(ThreadedModuleCore):
    """
    Generates random data for testing
    """

    def __init__(self):
        super().__init__()
        self.primary_module = True

        self.i = 0
        self.j = 0
        self.t = 0

        self.vehicle_position_filter = GPSPositionFilter("random data")

    def spin(self):
        self.i += 3
        if self.i > 360:
            self.i = 0

        self.j += 0.5
        if self.j > 360:
            self.j = 0
        r = random.random() * 0.1 + 0.95

        if self.i > 180:
            k = 10
        else:
            k = 0

        self.data_dictionary["roll"] = self.i
        self.data_dictionary["pitch"] = 10
        self.data_dictionary["yaw"] = self.i
        self.data_dictionary[Constants.altitude_key] = float(self.i) / 80.0 - 10
        self.data_dictionary["ground_speed"] = k
        self.data_dictionary["v_speed"] = (self.i / 15) - 10
        self.data_dictionary["acceleration"] = (self.i / 60) - 5
        self.data_dictionary["j"] = self.j
        self.data_dictionary["slowSweep"] = 1 - float(self.j) / 180.0

        # Generate lat-lon coords
        e = math.cos(math.radians(self.j)) * r * self.t
        n = math.sin(math.radians(self.j)) * r * self.t
        lla = navpy.ned2lla([n, e, 0], 42.3601, -71.0589, 0)
        self.vehicle_position_filter.new_gps_coords(lla[0], lla[1])
        [new_lat, new_lon] = self.vehicle_position_filter.get_filtered_position_output()
        self.data_dictionary[Constants.latitude_key] = new_lat
        self.data_dictionary[Constants.longitude_key] = new_lon

        self.data_dictionary["status"] = int((float(self.i) / 360.0) * 3)

        self.data_dictionary[Constants.fcb_battery_voltage] = ((float(self.i) / 360.0) * 5) + 11
        self.data_dictionary[Constants.fcb_memory_usage] = ((float(self.i) / 360.0) * 1)

        self.data_dictionary["pyro_continuity"] = [
            False,
            False,
            True,
            True,
            False,
            True,
        ]

        # Generate some state machine state names
        if self.i < 180:
            self.data_dictionary[Constants.fcb_state_key] = "Pre Launch :("
        else:
            self.data_dictionary[Constants.fcb_state_key] = "Flying :)"

        annunciator = [
            ["Overall", 0, "Test"],
            ["Battery", 1, "Test2"],
            ["Lights", 2, "Test3"],
            ["aaaaaaaaaaaaaaaaaaaaaaaaaa", 0, "test4"],
        ]
        self.data_dictionary["annunciator_1"] = annunciator

        diagnostics = {
            "aaa": [["hi", "aaa"], ["bbb", random.random()]],
            "bbb": [
                ["aa", "  {}".format(random.random())],
                ["bbb", random.random()],
                ["c", random.random()],
                ["ddddddddd", random.random()],
            ],
        }
        self.data_dictionary[Constants.raw_message_data_key] = diagnostics

        if self.i % 10 == 1:
            self.logToConsole(str(random.random()), int(random.random() * 3))

        time.sleep(0.02)

        self.t = self.t + 0.3
