"""
Core functions that need to run in the GUI thread, not the main thread
"""

import sys
import copy
import random
import serial.tools.list_ports

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QMenu

from Widgets import placeholder
from MainTabs.main_tab_common import TabCommon
from MainTabs.settings_tab import SettingsTab
from MainTabs.diagnostic_tab import DiagnosticTab
from MainTabs.rocket_primary_tab import RocketPrimaryTab

from Widgets import annunciator_panel
from Widgets import control_station_status
from Widgets import flight_display
from Widgets import map_widget
from Widgets import reconfigure_widget
from Widgets import simple_console_widget
from Widgets import text_box_drop_down_widget
from Widgets import vehicle_status_widget
from Widgets import video_widget

from data_helpers import get_rgb_from_string, get_well_formatted_rgb_string, format_rgb_string, make_stylesheet_string

# Background, Widget Background, Text, Header Text, Border
THEMES = {}
THEMES["Dark"] = ["rgb[13, 17, 23]", "rgb[13, 17, 23]", "rgb[139,148,158]", "rgb[88,166,255]", "rgb[139,148,158]"]
THEMES["Light"] = ["rgb[255, 255, 255]", "rgb[255, 255, 255]", "rgb[0,0,0]", "rgb[0,0,0]", "rgb[0,0,0]"]
THEMES["High Contrast Dark"] = ["rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[255,255,255]", "rgb[255,255,255]", "rgb[255,255,255]"]


class GUICore(object):
    def __init__(self):
        self.tabs = {}
        self.tabNames = []
        self.vehicleTabNames = []
        self.placeHolderList = []
        self.callback_queue = []

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

        self.serial_port_menu = QMenu()

        # Code to do dynamic creation of classes
        # The names are for humans, so they don't have to be the class name or anything
        self.widgetClasses = {}
        self.widgetClasses["Annunciator Panel"] = annunciator_panel.AnnunciatorPanel
        self.widgetClasses["Control Station Status"] = control_station_status.ControlStationStatus
        self.widgetClasses["Flight Display"] = flight_display.FlightDisplay
        self.widgetClasses["Map Widget"] = map_widget.MapWidget
        self.widgetClasses["Reconfigure"] = reconfigure_widget.ReconfigureWidget
        self.widgetClasses["Simple Console"] = simple_console_widget.SimpleConsoleWidget
        self.widgetClasses["Diagnostic Panel"] = text_box_drop_down_widget.TextBoxDropDownWidget
        self.widgetClasses["Vehicle Status"] = vehicle_status_widget.VehicleStatusWidget
        self.widgetClasses["Video Panel"] = video_widget.VideoWidget

        self.setUpMenuBar()

        self.application.setObjectName("Application")
        self.mainWindow.setObjectName("Main_Window")
        self.mainWindow.menuBar().setObjectName("Menu_Bar")
        self.tabHolderWidget.setObjectName("Tab_Holder")
        self.tabHolderWidget.tabBar().setObjectName("Tab_Bar")

    def start(self):
        # Generate a random title from this list
        # I don't know why I did this
        titles = ["DPF Ground Station"]
        self.title = random.choice(titles)

        self.mainWindow.setCentralWidget(self.tabHolderWidget)
        self.mainWindow.show()
        self.mainWindow.setWindowTitle(self.title)

        self.mainWindow.resize(1920, 1080)

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

        self.placeHolderList.append(placeholder.Placeholder(self.tabs[name]))  # Something needs to be updating for the GUI to function, so we make a silly thing to always do that

    def update(self, data, rosConsole):
        callbacks = []

        for widget in self.placeHolderList:
            widget.update()

        for tab in self.tabObjects:
            callbacks += tab.update(data, self.controlStationData, rosConsole)

        tabIndex = self.tabHolderWidget.currentIndex()
        activeTab = self.tabHolderWidget.tabText(tabIndex)
        self.mainWindow.setWindowTitle("[{0}] - {1}".format(activeTab, self.title))

        callbacks += copy.deepcopy(self.callback_queue)
        self.callback_queue = []

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

        self.serial_port_menu = menuBar.addMenu("Serial Port")
        self.serial_port_menu.aboutToShow.connect(self.refreshSerialPorts)  # aboutToShow runs before the menu is created
        serial_ports = [comport.device for comport in serial.tools.list_ports.comports()]
        for port in serial_ports:
            self.serial_port_menu.addAction(port, lambda portName=port: self.setActiveSerialPort(portName))

    def setActiveSerialPort(self, portName):
        self.callback_queue.append(["set_serial_port", portName])

    def refreshSerialPorts(self):
        serial_ports = [comport.device for comport in serial.tools.list_ports.comports()]
        self.serial_port_menu.clear()
        for port in serial_ports:
            self.serial_port_menu.addAction(port, lambda portName=port: self.setActiveSerialPort(portName))

    def createWidgetFromName(self, widgetName, parent=None):
        """Will create any widget from its file name!"""
        if widgetName not in self.widgetClasses:
            print("No widget of type {}".format(widgetName))
            return QWidget(parent)  # Kind of a hack
        try:
            widget = self.widgetClasses[widgetName](parent)
            return widget
        except all as e:
            print("Dynamically creating {} type widgets is not supported yet".format(widgetName))
            print(e)
            return QWidget(parent)

    def makeNewWidgetInCurrentTab(self, name):
        if name in self.widgetClasses:
            activeTab = self.getActiveTabObject()
            if activeTab is not None:
                activeTab.addWidget(self.createWidgetFromName(name, parent=activeTab.tabMainWidget))
                activeTab.updateTheme()
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
        elif tabType == "diagnostic":
            self.addVehicleTab(DiagnosticTab, tabName)
        elif tabType == "rocket_primary":
            self.addVehicleTab(RocketPrimaryTab, tabName)
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

        self.backgroundColor = get_well_formatted_rgb_string(background)
        self.widgetBackgroundColor = get_well_formatted_rgb_string(widgetBackground)
        self.textColor = get_well_formatted_rgb_string(text)
        self.headerTextColor = get_well_formatted_rgb_string(headerText)
        self.borderColor = get_well_formatted_rgb_string(border)

        [red, green, blue] = get_rgb_from_string(background)
        slightlyDarkerColor = format_rgb_string(max(red - 10, 0), max(green - 10, 0), max(blue - 10, 0))

        self.mainWindow.setStyleSheet("QWidget#" + self.mainWindow.objectName() + "{" + make_stylesheet_string("background", slightlyDarkerColor) + make_stylesheet_string("color", self.textColor) + "}")
        self.tabHolderWidget.setStyleSheet("QWidget#" + self.tabHolderWidget.objectName() + "{" + make_stylesheet_string("background", self.backgroundColor) + make_stylesheet_string("color", self.textColor) + "}")
        self.mainWindow.menuBar().setStyleSheet("QWidget#" + self.mainWindow.menuBar().objectName() + "{" + make_stylesheet_string("background", slightlyDarkerColor) + make_stylesheet_string("color", self.textColor) + "}")
        self.tabHolderWidget.tabBar().setStyleSheet("QWidget#" + self.tabHolderWidget.tabBar().objectName() + "{" + make_stylesheet_string("background", slightlyDarkerColor) + make_stylesheet_string("color", self.textColor) + "}")

        if sys.platform == "win32":
            self.tabHolderWidget.tabBar().setStyleSheet("QTabBar::tab{ background: " + get_well_formatted_rgb_string(background) + "; color: " + get_well_formatted_rgb_string(text) + "}")  # Seems to sort of fix tab bar coloring issues on windows

        for tab in self.tabObjects:
            tab.setTheme(self.backgroundColor, self.widgetBackgroundColor, self.textColor, self.headerTextColor, self.borderColor)
