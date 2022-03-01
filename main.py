#!/usr/bin/env python3

"""
Main file to run the GUI
"""

from dpf_ground_station import DPFGUI
from Modules.random_data_interface import RandomDataInterface
from Modules.ground_station_data_interface import GroundStationDataInterface
from Modules.ground_station_recorded_data_interface import GroundStationRecordedDataInterface
from Modules.android_phone_bluetooth_interface import AndroidPhoneBluetoothInterface
from Modules.laptop_status_monitor import LaptopStatusMonitor
from Modules.fake_rocket_flight import FakeFlight

if __name__ == '__main__':
    GUI = DPFGUI()
    GUI.addDataInterface("Serial Ground Station", GroundStationDataInterface(GUI))
    GUI.addDataInterface("Android Phone Bluetooth", AndroidPhoneBluetoothInterface())
    GUI.addDataInterface("Laptop Status Monitor", LaptopStatusMonitor())
    GUI.addDataInterface("Ground Station Recorded Data", GroundStationRecordedDataInterface(), enabled=False)
    GUI.addDataInterface("Random Data for Debugging", RandomDataInterface(), enabled=False)
    GUI.addDataInterface("Fake Flight", FakeFlight(), enabled=False)
    GUI.run()
    print("Good Bye")
