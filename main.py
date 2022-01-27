#!/usr/bin/env python3

"""
Main file to run the GUI
"""

from dpf_ground_station import DPFGUI

if __name__ == '__main__':
    GUI = DPFGUI(multi_robot_tab=False)
    GUI.addVehicle("warpauv", "warpauv")
    GUI.run()
    print("Good Bye")
