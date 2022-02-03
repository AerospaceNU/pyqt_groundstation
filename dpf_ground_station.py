"""
Central GUI sequencer

Has all the thread control for the GUI
"""

import copy

from PyQt5.QtCore import QTimer

from DataInterfaces.data_interface_core import DataInterfaceCore
from gui_core import GUICore


class DPFGUI():
    def __init__(self, multi_robot_tab=True):
        self.GUIStarted = False
        self.GUIStopCommanded = False
        self.isRunning = True
        self.multiRobot = multi_robot_tab

        self.vehicleData = {}
        self.ConsoleData = [[]]
        self.callbacks = []
        self.callbackFunctions = {}

        self.data_interfaces = {}

        self.GUICore = GUICore()

    def run(self):
        self.GUICore.addTabByTabType("settings", "Settings")

        self.addTab("Primary", "rocket_primary")
        # self.addTab("Old", "primary")
        self.addTab("Diagnostic", "diagnostic")

        self.GUICore.setThemeByName("Dark")

        # QTimer to run the update method
        timer = QTimer()
        timer.timeout.connect(self.updateGUI)
        timer.start(20)

        self.GUIStarted = True
        self.GUICore.start()

        # This happens after the GUI closes
        self.isRunning = False
        self.stop()

    def updateGUI(self):
        """Runs in GUI thread every 20ms"""
        if self.GUIStopCommanded:
            self.stop()

        # Get data from interfaces
        for interface in self.data_interfaces:
            temp_dictionary = self.data_interfaces[interface].getDataDictionary()
            self.vehicleData.update(temp_dictionary.copy())

        self.callbacks += self.GUICore.update(self.vehicleData, self.ConsoleData)

    def updateVehicleData(self, vehicleName, data):
        """Called in the main thread"""
        self.vehicleData[vehicleName] = data

    def updateConsole(self, value, level):
        self.ConsoleData = ([[value, level]] + self.ConsoleData)[:40]

    def processCallbacks(self):
        callbacks = copy.deepcopy(self.callbacks)
        self.callbacks = []

        for callback in callbacks:
            if callback[0] in self.callbackFunctions:
                self.callbackFunctions[callback[0]](callback[1])  # <sarcasm>What amazingly clean code</sarcasm>
            else:
                pass
                # print("{} isn't a valid callback".format(callback[0])) # Debugging code
                # print(self.callbackFunctions.keys())

    def addCallback(self, target, callback):
        self.callbackFunctions[target] = callback

    def stop(self):
        for interface in self.data_interfaces:
            self.data_interfaces[interface].stop()

        self.GUICore.stop()

    def addTab(self, tabName, tabType):
        self.GUICore.addTabByTabType(tabType, tabName)

    def addDataInterface(self, interface_name: str, interface_object: DataInterfaceCore, enabled=True):
        self.data_interfaces[interface_name] = interface_object
        interface_object.setConsoleCallback(self.updateConsole)
        interface_object.setEnabled(enabled)
        interface_object.start()
