#!/usr/bin/env python3

"""
Main file to run the GUI
"""

from dpf_ground_station import DPFGUI
from DataInterfaces.random_data_interface import RandomDataInterface

if __name__ == '__main__':
    random_interface = RandomDataInterface()

    GUI = DPFGUI(multi_robot_tab=False)
    GUI.addDataInterface("random", random_interface)
    GUI.run()
    print("Good Bye")
