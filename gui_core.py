"""
Core functions that need to run in the GUI thread, not the main thread
"""

import inspect
import types

import random

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget

from Widgets import Placeholder
from MainTabs.main_tab_common import TabCommon
from MainTabs.settings_tab import SettingsTab
from MainTabs.primary_tab import PrimaryTab

from Widgets import *

from data_helpers import getRGBFromString, getWellFormattedRGBString, formatRGBString, makeStylesheetString

# Background, Widget Background, Text, Header Text, Border
THEMES = {}
THEMES["Dark"] = ["rgb[13, 17, 23]", "rgb[13, 17, 23]", "rgb[139,148,158]", "rgb[88,166,255]", "rgb[139,148,158]"]
THEMES["Light"] = ["rgb[255, 255, 255]", "rgb[255, 255, 255]", "rgb[0,0,0]", "rgb[0,0,0]", "rgb[0,0,0]"]
THEMES["High Contrast Dark"] = ["rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[255,255,255]", "rgb[255,255,255]", "rgb[255,255,255]"]
THEMES["For hardware labs only"] = ["rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[0,0,0]", "rgb[0,0,0]", "rgb[0,0,0]"]


class GUICore(object):
    def __init__(self):
        self.tabs = {}
        self.tabNames = []
        self.vehicleTabNames = []
        self.widgetList = []
        self.placeHolderList = []

        self.tabObjects = []
        self.controlStationData = {}

        self.title = ""

        self.backgroundColor = ""
        self.widgetBackgroundColor = ""
        self.textColor = ""
        self.headerTextColor = ""
        self.borderColor = ""

        self.application = QApplication([])
        self.mainWindow = QMainWindow()
        self.tabHolderWidget = QTabWidget()

        # Code to do dynamic creation of classes
        self.widgetClasses = {}
        excluded = ["__", "Placeholder", "WidgetClasses.QWidgets", "QWidget_Parts", "Helpers", "CustomQWidget"]
        for name, val in globals().items():  # Loop through globals()
            if isinstance(val, types.ModuleType) and "Widgets." in str(val):  # Only look at modules from Widgets
                for item in inspect.getmembers(val):
                    containsExcludedStrings = False
                    for a in excluded:
                        if a in str(item):
                            containsExcludedStrings = True
                            break

                    if name in str(item) and not containsExcludedStrings:
                        self.widgetClasses[name] = item[1]

        self.setUpMenuBar()

        self.application.setObjectName("Application")
        self.mainWindow.setObjectName("Main_Window")
        self.mainWindow.menuBar().setObjectName("Menu_Bar")
        self.tabHolderWidget.setObjectName("Tab_Holder")
        self.tabHolderWidget.tabBar().setObjectName("Tab_Bar")

        self.mainWindow.resize(1920, 1080)

    def start(self):
        # Generate a random title from this list
        # I don't know why I did this
        titles = ["DPF Ground Station"]
        self.title = random.choice(titles)

        self.mainWindow.setCentralWidget(self.tabHolderWidget)
        self.mainWindow.show()
        self.mainWindow.setWindowTitle(self.title)
        self.application.exec_()

    def stop(self):
        print("Stopping GUI")
        self.application.exit()
        exit(0)

    def createTab(self, name):
        """Creates a tab with the specified name"""
        self.tabs[name] = QWidget()
        self.tabs[name].setObjectName(name)

        self.tabHolderWidget.addTab(self.tabs[name], name)
        self.tabNames.append(name)

        self.placeHolderList.append(Placeholder.Placeholder(self.tabs[name]))  # Something needs to be updating for the GUI to function, so we make a silly thing to always do that

    def update(self, data, rosConsole):
        callbacks = []

        for widget in self.placeHolderList:
            widget.update()

        for tab in self.tabObjects:
            callbacks += tab.update(data, self.controlStationData, rosConsole)

        return callbacks

    def updateControlStationData(self, data):
        self.controlStationData = data

    def setUpMenuBar(self):
        """Create menu bar"""
        menuBar = self.mainWindow.menuBar()
        fileMenu = menuBar.addMenu("File")
        fileMenu.addAction("Quit", self.stop)

        # Menu bar for widgets
        widgetMenu = menuBar.addMenu("Add")

        for item in self.widgetClasses:
            widgetMenu.addAction(item, lambda name=item: self.makeNewWidgetInCurrentTab(name))
        widgetMenu.addSeparator()

        themeMenu = menuBar.addMenu("Theme")
        for theme in THEMES:
            themeMenu.addAction(theme, lambda themeName=theme: self.setThemeByName(themeName))

    def makeNewWidgetInCurrentTab(self, name):
        if name in self.widgetClasses:
            activeTab = self.getActiveTabObject()
            if activeTab is not None:
                pass
                # activeTab.addWidgetToActiveSubTab(name)
        else:
            print("No widget named {}".format(name))

    def getActiveTabObject(self) -> TabCommon:
        tabIndex = self.tabHolderWidget.currentIndex()
        activeTab = self.tabHolderWidget.tabText(tabIndex)

        if activeTab in self.vehicleTabNames:
            return self.tabObjects[self.vehicleTabNames.index(activeTab)]
        else:
            return None

    def addTabByTabType(self, tabType: str, tabName: str):
        if tabType == "settings":
            self.addVehicleTab(SettingsTab, tabName)
        elif tabType == "primary":
            self.addVehicleTab(PrimaryTab, tabName)
        else:
            print("Don't have tab configuration for vehicle type {}".format(tabType))

    def addVehicleTab(self, tab, vehicleName: str):
        self.createTab(vehicleName)
        self.tabObjects.append(tab(self.tabs[vehicleName], vehicleName))
        self.vehicleTabNames.append(vehicleName)
        self.tabObjects[-1].setTheme(self.backgroundColor, self.widgetBackgroundColor, self.textColor, self.headerTextColor, self.borderColor)
        self.tabHolderWidget.setCurrentIndex(self.tabHolderWidget.count() - 1)
        self.tabHolderWidget.setCurrentIndex(1)

    def setThemeByName(self, name: str):
        if name in THEMES:
            theme = THEMES[name]
            self.setTheme(theme[0], theme[1], theme[2], theme[3], theme[4])
            if name == "For hardware labs only":  # Silly stuff
                self.title = "We're not a hardware lab"
        else:
            print("No Theme named {}".format(name))

    def setTheme(self, background: str, widgetBackground: str, text: str, headerText: str, border: str):
        """
        Sets theme from given color strings.  Currently the only accpted format for color strings is rgb(red,green,blue), but I'm going to add more at some point.

        :param background: Background color for the GUI
        :param widgetBackground: Widget color
        :param text: Primary text color
        :param headerText: Header text color
        :param border: Widget border color
        """

        self.backgroundColor = getWellFormattedRGBString(background)
        self.widgetBackgroundColor = getWellFormattedRGBString(widgetBackground)
        self.textColor = getWellFormattedRGBString(text)
        self.headerTextColor = getWellFormattedRGBString(headerText)
        self.borderColor = getWellFormattedRGBString(border)

        [red, green, blue] = getRGBFromString(background)
        slightlyDarkerColor = formatRGBString(max(red - 10, 0), max(green - 10, 0), max(blue - 10, 0))

        self.mainWindow.setStyleSheet("QWidget#" + self.mainWindow.objectName() + "{" + makeStylesheetString("background", slightlyDarkerColor) + makeStylesheetString("color", self.textColor) + "}")
        self.tabHolderWidget.setStyleSheet("QWidget#" + self.tabHolderWidget.objectName() + "{" + makeStylesheetString("background", self.backgroundColor) + makeStylesheetString("color", self.textColor) + "}")
        self.mainWindow.menuBar().setStyleSheet("QWidget#" + self.mainWindow.menuBar().objectName() + "{" + makeStylesheetString("background", slightlyDarkerColor) + makeStylesheetString("color", self.textColor) + "}")
        self.tabHolderWidget.tabBar().setStyleSheet("QWidget#" + self.tabHolderWidget.tabBar().objectName() + "{" + makeStylesheetString("background", slightlyDarkerColor) + makeStylesheetString("color", self.textColor) + "}")

        for tab in self.tabObjects:
            tab.setTheme(self.backgroundColor, self.widgetBackgroundColor, self.textColor, self.headerTextColor, self.borderColor)
