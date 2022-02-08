"""
Generates random data for testing
"""

import math
import random

from constants import Constants

from DataInterfaces.data_interface_core import DataInterfaceCore


class RandomDataInterface(DataInterfaceCore):
    def __init__(self):
        super().__init__()
        self.i = 0
        self.j = 0

    def spin(self):
        self.i += 3
        if self.i > 360:
            self.i = 0

        self.j += 0.5
        if self.j > 360:
            self.j = 0
        r = random.random() * 0.1 + 0.95

        self.data_dictionary["roll"] = self.i
        self.data_dictionary["pitch"] = 10
        self.data_dictionary["yaw"] = self.i
        self.data_dictionary[Constants.altitude_key] = float(self.i) / 80.0 - 10
        self.data_dictionary["groundSpeed"] = 19.5
        self.data_dictionary["verticalSpeed"] = (self.i / 15) - 10
        self.data_dictionary["acceleration"] = (self.i / 60) - 5
        self.data_dictionary["j"] = self.j
        self.data_dictionary["slowSweep"] = 1 - float(self.j) / 180.0
        self.data_dictionary["x_position_global"] = math.cos(math.radians(self.j)) * r
        self.data_dictionary["y_position_global"] = math.sin(math.radians(self.j)) * r

        self.data_dictionary["status"] = int((float(self.i) / 360.0) * 3)
        self.data_dictionary["fcb_battery_voltage"] = ((float(self.i) / 360.0) * 5) + 13

        # Generate some state machine state names
        if self.i < 180:
            self.data_dictionary[Constants.fcb_state_key] = "Pre Launch :("
        else:
            self.data_dictionary[Constants.fcb_state_key] = "Flying :)"

        annunciator = [["Overall", 0, "Test"], ["Battery", 1, "Test2"], ["Lights", 2, "Test3"], ["aaaaaaaaaaaaaaaaaaaaaaaaaa", 0, "test4"]]
        self.data_dictionary["annunciator_1"] = annunciator

        diagnostics = {"aaa": [["hi", "aaa"], ["bbb", random.random()]], "bbb": [["aa", "  {}".format(random.random())], ["bbb", random.random()], ["c", random.random()], ["ddddddddd", random.random()]]}
        self.data_dictionary["diagnostics"] = diagnostics

        if self.i % 10 == 1:
            self.logToConsole(str(random.random()), int(random.random() * 3))
