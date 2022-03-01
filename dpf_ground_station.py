"""
Central GUI sequencer

Has all the thread control for the GUI
"""

import copy
import random
import sys
import serial.tools.list_ports

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QMenu

from Modules.data_interface_core import ThreadedModuleCore

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
THEMES["Don't click on this one"] = ["rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[0, 0, 0]"]


class DPFGUI():
    def __init__(self):
        self.GUIStopCommanded = False

        # This could use some restructuring
        self.database_dictionary = {}
        self.ConsoleData = [[]]
        self.callbackFunctions = {}
        self.callback_queue = []
        self.data_interface_dict = {}

        self.tabs = {}
        self.tabNames = []
        self.vehicleTabNames = []
        self.placeHolderList = []
        self.tabObjects = []

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
        self.data_interface_menu = QMenu()

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

        self.application.setObjectName("Application")
        self.mainWindow.setObjectName("Main_Window")
        self.mainWindow.menuBar().setObjectName("Menu_Bar")
        self.tabHolderWidget.setObjectName("Tab_Holder")
        self.tabHolderWidget.tabBar().setObjectName("Tab_Bar")

    def run(self):
        # Add tabs to GUI
        self.addTabByTabType("settings", "Settings")
        self.addTabByTabType("rocket_primary", "Primary")
        self.addTabByTabType("diagnostic", "Diagnostic")

        # Add callback to clear console
        self.addCallback("clear_console", self.clearConsole)

        # Other setup tasks
        self.setThemeByName("Dark")
        self.setUpMenuBar()

        # Generate a random title from this list
        # I don't know why I did this
        titles = ["DPF Ground Station", "Make sure the pointy end is facing up", "This title intentionally left blank", "Don't crash the rocket"]
        self.title = random.choice(titles)

        # Set up main window
        self.mainWindow.setCentralWidget(self.tabHolderWidget)
        self.mainWindow.setWindowTitle(self.title)
        self.mainWindow.resize(1920, 1080)

        # QTimer to run the update method
        timer = QTimer()
        timer.timeout.connect(self.updateGUI)
        timer.start(20)

        # Run (blocks until GUI closes)
        self.mainWindow.show()
        self.application.exec_()

        # This happens after the GUI closes
        self.stop()

    def setUpMenuBar(self):
        """Create menu bar"""

        # Get main menu bar object
        menuBar = self.mainWindow.menuBar()
        fileMenu = menuBar.addMenu("File")
        fileMenu.addAction("Quit", self.stop)

        # Menu bar to add new widgets
        widgetMenu = menuBar.addMenu("Add")

        for item in self.widgetClasses:
            widgetMenu.addAction(item, lambda name=item: self.makeNewWidgetInCurrentTab(name))
        widgetMenu.addSeparator()

        # Menu bar to change theme
        themeMenu = menuBar.addMenu("Theme")
        for theme in THEMES:
            themeMenu.addAction(theme, lambda themeName=theme: self.setThemeByName(themeName))

        # Menu bar to set serial port
        # Because the available serial ports and data interfaces change after this class is created, we run a method every time we create the menu
        self.serial_port_menu = menuBar.addMenu("Serial Port")
        self.serial_port_menu.aboutToShow.connect(self.refreshSerialPorts)  # aboutToShow runs before the menu is created

        # Menu bar to enable/disable data interfaces
        self.data_interface_menu = menuBar.addMenu("Data Interfaces")
        self.data_interface_menu.aboutToShow.connect(self.refreshDataInterfaces)

    def setActiveSerialPort(self, portName):
        self.callback_queue.append(["set_serial_port", portName])

    def enableDisableDataInterface(self, interfaceName):
        interface = self.data_interface_dict[interfaceName]
        interface.toggleEnabled()

    def refreshDataInterfaces(self):
        self.data_interface_menu.clear()

        for interfaceName in self.data_interface_dict:
            interface = self.data_interface_dict[interfaceName]
            if interface.enabled:
                self.data_interface_menu.addAction("Disable {}".format(interfaceName), lambda targetInterface=interfaceName: self.enableDisableDataInterface(targetInterface))
            else:
                self.data_interface_menu.addAction("Enable {}".format(interfaceName), lambda targetInterface=interfaceName: self.enableDisableDataInterface(targetInterface))

    def refreshSerialPorts(self):
        serial_ports = [comport.device for comport in serial.tools.list_ports.comports()]
        self.serial_port_menu.clear()
        for port in serial_ports:
            self.serial_port_menu.addAction(port, lambda portName=port: self.setActiveSerialPort(portName))

    def updateGUI(self):
        """Runs in GUI thread every 20ms"""
        if self.GUIStopCommanded:
            self.stop()

        # Get data from interfaces
        for interface in self.data_interface_dict:
            self.database_dictionary.update(self.data_interface_dict[interface].getDataDictionary().copy())

        # Send full database dictionary back to the data interfaces
        for interface in self.data_interface_dict:
            self.data_interface_dict[interface].setFullDataDictionary(copy.deepcopy(self.database_dictionary))

        # Update placeholder widgets
        for widget in self.placeHolderList:
            widget.update()

        # Update tabs
        for tab in self.tabObjects:
            self.callback_queue += tab.update(self.database_dictionary, self.ConsoleData)

        # set window title
        tabIndex = self.tabHolderWidget.currentIndex()
        activeTab = self.tabHolderWidget.tabText(tabIndex)
        self.mainWindow.setWindowTitle("[{0}] - {1}".format(activeTab, self.title))

        # Process callbacks
        self.processCallbacks()

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

    def createTab(self, name):
        """Creates a tab with the specified name"""
        self.tabs[name] = QWidget()
        self.tabs[name].setObjectName(name)

        self.tabHolderWidget.addTab(self.tabs[name], name)
        self.tabNames.append(name)

        self.placeHolderList.append(placeholder.Placeholder(self.tabs[name]))  # Something needs to be updating for the GUI to function, so we make a silly thing to always do that

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

    def updateVehicleData(self, keyName, data):
        """Called in the main thread"""
        self.database_dictionary[keyName] = data

    def updateConsole(self, value, level):
        self.ConsoleData = ([[value, level]] + self.ConsoleData)[:40]

    def processCallbacks(self):
        callbacks = copy.deepcopy(self.callback_queue)
        self.callback_queue = []

        for callback in callbacks:
            if callback[0] in self.callbackFunctions:
                self.callbackFunctions[callback[0]](callback[1])  # <sarcasm>What amazingly clean code</sarcasm>
            else:
                pass
                # print("{} isn't a valid callback".format(callback[0]))  # Debugging code
                # print(self.callbackFunctions.keys())

    def addCallback(self, target, callback):
        self.callbackFunctions[target] = callback

    def addDataInterface(self, interface_name: str, interface_object: ThreadedModuleCore, enabled=True):
        self.data_interface_dict[interface_name] = interface_object
        interface_object.setConsoleCallback(self.updateConsole)
        interface_object.setEnabled(enabled)
        interface_object.start()

    def clearConsole(self, _):  # Need a empty arg to fit with callback system
        self.ConsoleData = [[]]

    def stop(self):
        for interface in self.data_interface_dict:
            self.data_interface_dict[interface].stop()

        self.application.exit()
