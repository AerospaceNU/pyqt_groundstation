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
from Modules.egg_finder_radio_interface import EggFinderRadioInterface
from Modules.fcb_offload_module import FCBOffloadModule

if __name__ == '__main__':
    # Make GUI object, but don't start it yet
    GUI = DPFGUI()

    # Add tabs to GUI
    GUI.addTabByTabType("Settings", "Settings")
    GUI.addTabByTabType("Rocket Primary", "Primary")
    GUI.addTabByTabType("Diagnostic", "Diagnostic")
    GUI.addTabByTabType("Graph", "Graphs")
    GUI.addTabByTabType("Offload", "Offload")

    # Load in modules
    GUI.addModule("Serial Ground Station", GroundStationDataInterface, enabled=True)
    GUI.addModule("Egg Finder Radio", EggFinderRadioInterface, enabled=False)
    GUI.addModule("FCB Offload", FCBOffloadModule, enabled=False)
    GUI.addModule("Android Phone Bluetooth", AndroidPhoneBluetoothInterface)
    GUI.addModule("Text To Speech", TextToSpeech, enabled=False)
    GUI.addModule("Laptop Status Monitor", LaptopStatusMonitor, hide_toggle=True)
    GUI.addModule("Local Simulation", LocalSimulationFlightInterface, enabled=False)
    GUI.addModule("Ground Station Recorded Data", GroundStationRecordedDataInterface, enabled=False)
    GUI.addModule("Fake Flight", FakeFlight, enabled=False)
    GUI.addModule("Random Data for Debugging", RandomDataInterface, enabled=False, hide_toggle=False)
    GUI.addModule("Map Interface", MapInterface, enabled=True, hide_toggle=True)

    # Run GUI, and wait until its killed
    GUI.run()
    print("Good Bye")
