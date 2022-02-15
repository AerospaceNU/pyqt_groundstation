#!/usr/bin/env python3

"""
Main file to run the GUI
"""

from dpf_ground_station import DPFGUI
from DataInterfaces.random_data_interface import RandomDataInterface
from DataInterfaces.ground_station_data_interface import GroundStationDataInterface
from DataInterfaces.ground_station_recorded_data_interface import GroundStationRecordedDataInterface

if __name__ == '__main__':
    GUI = DPFGUI()
    GUI.addDataInterface("random", RandomDataInterface(), enabled=False)
    GUI.addDataInterface("ground_station", GroundStationDataInterface(GUI))
    GUI.addDataInterface("ground_station_recorded_data", GroundStationRecordedDataInterface(), enabled=False)
    GUI.run()
    print("Good Bye")
