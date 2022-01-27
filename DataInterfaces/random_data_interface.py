"""
Generates random data for testing
"""

import math
import random

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
        self.data_dictionary["depth"] = float(self.i) / 80.0 - 10
        self.data_dictionary["groundSpeed"] = 19.5
        self.data_dictionary["verticalSpeed"] = (self.i / 15) - 10
        self.data_dictionary["terrainAlt"] = (-self.i / 5) + 40
        self.data_dictionary["j"] = self.j
        self.data_dictionary["slowSweep"] = 1 - float(self.j) / 180.0
        self.data_dictionary["x_position_global"] = math.cos(math.radians(self.j)) * r
        self.data_dictionary["y_position_global"] = math.sin(math.radians(self.j)) * r

        self.data_dictionary["status"] = int((float(self.i) / 360.0) * 3)
        self.data_dictionary["battery_percent"] = (float(self.i) / 360.0)
        self.data_dictionary["battery_voltage"] = ((float(self.i) / 360.0) * 5) + 13
        self.data_dictionary["battery_current"] = ((float(self.i) / 360.0) * 30)
