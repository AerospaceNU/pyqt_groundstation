#!/usr/bin/env python3

"""
Main file to run the GUI
"""

from dpf_ground_station import DPFGUI
from DataInterfaces.random_data_interface import RandomDataInterface
from DataInterfaces.ground_station_data_interface import GroundStationDataInterface
from DataInterfaces.ground_station_recorded_data_interface import GroundStationRecordedDataInterface
from DataInterfaces.android_phone_bluetooth_interface import AndroidPhoneBluetoothInterface
from DataInterfaces.laptop_status_monitor import LaptopStatusMonitor

if __name__ == '__main__':
    GUI = DPFGUI()
    GUI.addDataInterface("random", RandomDataInterface(), enabled=False)
    GUI.addDataInterface("ground_station", GroundStationDataInterface(GUI))
    GUI.addDataInterface("ground_station_recorded_data", GroundStationRecordedDataInterface(), enabled=False)
    GUI.addDataInterface("android_phone_bluetooth", AndroidPhoneBluetoothInterface())
    GUI.addDataInterface("laptop_status_monitor", LaptopStatusMonitor())
    GUI.run()
    print("Good Bye")
