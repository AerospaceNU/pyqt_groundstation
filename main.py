#!/usr/bin/env python3

"""
Main file to run the GUI
"""

from dpf_ground_station import DPFGUI
from Modules.random_data_interface import RandomDataInterface
from Modules.ground_station_data_interface import GroundStationDataInterface
from Modules.desktop_simulation_interface import LocalSimulationFlightInterface
from Modules.ground_station_recorded_data_interface import GroundStationRecordedDataInterface
from Modules.android_phone_bluetooth_interface import AndroidPhoneBluetoothInterface
from Modules.laptop_status_monitor import LaptopStatusMonitor
from Modules.fake_rocket_flight import FakeFlight
from Modules.text_to_speech import TextToSpeech
from Modules.map_interface import MapInterface

if __name__ == '__main__':
    GUI = DPFGUI()

    # Add tabs to GUI
    GUI.addTabByTabType("settings", "Settings")
    GUI.addTabByTabType("rocket_primary", "Primary")
    GUI.addTabByTabType("diagnostic", "Diagnostic")
    GUI.addTabByTabType("graph", "Graphs")

    # Load in modules
    GUI.addModule("Serial Ground Station", GroundStationDataInterface, enabled=True)
    GUI.addModule("Android Phone Bluetooth", AndroidPhoneBluetoothInterface)
    GUI.addModule("Text To Speech", TextToSpeech, enabled=False)
    GUI.addModule("Laptop Status Monitor", LaptopStatusMonitor, hide_toggle=True)
    GUI.addModule("Local Simulation", LocalSimulationFlightInterface, enabled=False)
    GUI.addModule("Ground Station Recorded Data", GroundStationRecordedDataInterface, enabled=False)
    GUI.addModule("Fake Flight", FakeFlight, enabled=False)
    GUI.addModule("Random Data for Debugging", RandomDataInterface, enabled=False, hide_toggle=False)
    GUI.addModule("Map Interface", MapInterface, enabled=True, hide_toggle=True)

    GUI.run()
    print("Good Bye")
