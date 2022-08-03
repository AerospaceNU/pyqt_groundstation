#!/usr/bin/env python3

"""
Main file to run the GUI
"""

import sys

from src.constants import Constants
from src.dpf_ground_station import DPFGUI
from src.Modules.android_phone_bluetooth_interface import AndroidPhoneBluetoothInterface
from src.Modules.desktop_simulation_interface import LocalSimulationFlightInterface
from src.Modules.egg_finder_radio_interface import EggFinderRadioInterface
from src.Modules.fake_rocket_flight import FakeFlight
from src.Modules.fcb_offload_module import FCBOffloadModule
from src.Modules.ground_station_data_interface import GroundStationDataInterface
from src.Modules.ground_station_recorded_data_interface import (
    GroundStationRecordedDataInterface,
)
from src.Modules.laptop_status_monitor import LaptopStatusMonitor
from src.Modules.map_interface import MapInterface
from src.Modules.prop_websocket_interface import PropWebsocketInterface
from src.Modules.random_data_interface import RandomDataInterface
from src.Modules.text_to_speech import TextToSpeech

if __name__ == "__main__":
    # Make GUI object, but don't start it yet
    GUI = DPFGUI()

    # Add tabs to GUI
    GUI.addTabByTabType("Rocket Primary", "Primary")
    GUI.addTabByTabType("Diagnostic", "Diagnostic")
    GUI.addTabByTabType("Graph", "Graphs")
    GUI.addTabByTabType("Offload", "Offload")

    # OpenGL is really slow on everything but linux, it seems
    if sys.platform == "linux":
        GUI.addTabByTabType("Model Viewer", "AeroNU: The 3D Experience")

    GUI.addTabByTabType("Prop Control", "Prop Control")

    # Load in modules
    GUI.addModule("Serial Ground Station", GroundStationDataInterface, enabled=True)
    GUI.addModule("Egg Finder Radio", EggFinderRadioInterface, enabled=False)
    GUI.addModule("FCB Offload", FCBOffloadModule, enabled=False)
    GUI.addModule("Android Phone Bluetooth", AndroidPhoneBluetoothInterface, enabled=False)
    GUI.addModule("Text To Speech", TextToSpeech, enabled=False)
    GUI.addModule("Laptop Status Monitor", LaptopStatusMonitor, hide_toggle=True)
    GUI.addModule("Local Simulation", LocalSimulationFlightInterface, enabled=False)
    GUI.addModule("Ground Station Recorded Data", GroundStationRecordedDataInterface, enabled=False)
    GUI.addModule("Fake Flight", FakeFlight, enabled=False)
    GUI.addModule("Random Data for Debugging", RandomDataInterface, enabled=False, hide_toggle=False)
    GUI.addModule("Map Interface", MapInterface, enabled=True, hide_toggle=True)
    GUI.addModule(Constants.InterfaceNames.prop_websocket, PropWebsocketInterface, enabled=False, hide_toggle=False)

    GUI.loadSettings()

    # Run GUI, and wait until its killed
    GUI.run()
    print("Good Bye")
