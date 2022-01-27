"""
Central GUI sequencer

Has all the thread control for the GUI
"""

import copy

from PyQt5.QtCore import QTimer

from gui_core import GUICore


class DPFGUI():
    def __init__(self, multi_robot_tab=True):
        self.GUIStarted = False
        self.GUIStopCommanded = False
        self.isRunning = True
        self.activeVehicle = ""
        self.multiRobot = multi_robot_tab

        self.vehicleData = {}
        self.ROSConsole = [[]]
        self.callbacks = []
        self.callbackFunctions = {}

        self.tabsToAdd = []

        self.GUICore = GUICore()  # Need to define this inside the thread

    def run(self):
        self.GUICore.addTabByTabType("settings", "Settings")

        self.addTab("Primary", "primary")

        # Need to do themes better at some point, but this is good for now
        self.GUICore.setTheme("rgb[13, 17, 23]", "rgb[13, 17, 23]", "rgb[139,148,158]", "rgb[88,166,255]", "rgb[139,148,158]")

        # QTimer to run the update method
        timer = QTimer()
        timer.timeout.connect(self.updateGUI)
        timer.start(10)

        self.GUIStarted = True
        self.GUICore.start()

        # This happens after the GUI closes
        self.isRunning = False

    def updateGUI(self):
        """Runs in GUI thread every 10ms"""
        if self.GUIStopCommanded:
            self.stop()

        if len(self.tabsToAdd) > 0:  # Have to do the adding in this thread
            for request in self.tabsToAdd:
                self.GUICore.addTabByTabType(request[1], request[0])
            self.tabsToAdd = []

        self.callbacks += self.GUICore.update(self.vehicleData, self.ROSConsole)

        tabIndex = self.GUICore.tabHolderWidget.currentIndex()
        activeTab = self.GUICore.tabHolderWidget.tabText(tabIndex)

        if activeTab in self.GUICore.vehicleTabNames:
            self.activeVehicle = activeTab

        self.GUICore.mainWindow.setWindowTitle("[{0}] - {1}".format(self.activeVehicle, self.GUICore.title))

    def updateVehicleData(self, vehicleName, data):
        """Called in the main thread"""
        self.vehicleData[vehicleName] = data

    def updateROSConsole(self, value, level):
        self.ROSConsole = ([[value, level]] + self.ROSConsole)[:40]

    def processCallbacks(self):
        callbacks = copy.deepcopy(self.callbacks)
        self.callbacks = []

        for callback in callbacks:
            if callback[0] in self.callbackFunctions:
                self.callbackFunctions[callback[0]](callback[1])  # What amazingly clean code
            else:
                pass
                # print("{} isn't a valid callback".format(callback[0])) # Debugging code
                # print(self.callbackFunctions.keys())

    def addCallback(self, target, callback):
        self.callbackFunctions[target] = callback

    def stop(self):
        self.GUICore.stop()

    def getActiveVehicle(self):
        return self.activeVehicle

    def addTab(self, tabName, tabType):
        self.tabsToAdd.append([tabName, tabType])
