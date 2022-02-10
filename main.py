#!/usr/bin/env python3

"""
Main file to run the GUI
"""

from dpf_ground_station import DPFGUI
from DataInterfaces.random_data_interface import RandomDataInterface
from DataInterfaces.ground_station_data_interface import GroundStationDataInterface

if __name__ == '__main__':
    GUI = DPFGUI()
    GUI.addDataInterface("random", RandomDataInterface(), enabled=False)
    GUI.addDataInterface("ground_station", GroundStationDataInterface())
    GUI.run()
    print("Good Bye")
