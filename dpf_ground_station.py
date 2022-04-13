"""
Central GUI sequencer

Has all the thread control for the GUI
"""

import copy
import random
import sys
import time
import serial.tools.list_ports

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QMenu

from Modules.data_interface_core import ThreadedModuleCore

from Widgets import placeholder
from MainTabs.main_tab_common import TabCommon
from MainTabs.settings_tab import SettingsTab
from MainTabs.diagnostic_tab import DiagnosticTab
from MainTabs.rocket_primary_tab import RocketPrimaryTab
from MainTabs.graphs_tab import GraphsTab
from MainTabs.main_tab_common import TabCommon

from Widgets import annunciator_panel
from Widgets import control_station_status
from Widgets import flight_display
from Widgets import map_widget
from Widgets import reconfigure_widget
from Widgets import simple_console_widget
from Widgets import complete_console_widget
from Widgets import text_box_drop_down_widget
from Widgets import vehicle_status_widget
from Widgets import video_widget
from Widgets import graph_widget
from Widgets import pyro_display_widget
from Widgets import local_sim_widget
from Widgets import line_cutter_control

from data_helpers import get_rgb_from_string, get_well_formatted_rgb_string, format_rgb_string, make_stylesheet_string
from constants import Constants

# Background, Widget Background, Text, Header Text, Border
THEMES = {}
THEMES["Dark"] = ["rgb[13, 17, 23]", "rgb[13, 17, 23]", "rgb[139,148,158]", "rgb[88,166,255]", "rgb[139,148,158]"]
THEMES["No Borders"] = ["rgb[13, 17, 23]", "rgb[13, 17, 23]", "rgb[139,148,158]", "rgb[88,166,255]", "rgb[40,50,70]"]
THEMES["Green Text"] = ["rgb[20, 20, 20]", "rgb[25, 25, 25]", "rgb[150,150,150]", "rgb[10,200,10]", "rgb[50,50,50]"]
THEMES["Light"] = ["rgb[255, 255, 255]", "rgb[255, 255, 255]", "rgb[0,0,0]", "rgb[0,0,0]", "rgb[0,0,0]"]
THEMES["High Contrast Dark"] = ["rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[255,255,255]", "rgb[255,255,255]", "rgb[255,255,255]"]
THEMES["Don't click on this one"] = ["rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[0, 0, 0]", "rgb[0, 0, 0]"]


class DPFGUI():
    def __init__(self):
        self.GUIStopCommanded = False

        # This could use some restructuring
        self.database_dictionary = {}
        self.updated_data_dictionary = {}  # Tracks which keys are new since the last GUI loop
        self.ConsoleData = [[]]
        self.callbackFunctions = {}
        self.callback_queue = []
        self.module_dictionary = {}
        self.module_load_time_dictionary = {}
        self.hidden_modules = []
        self.playback_data_sources = []
        self.current_playback_source = ""

        self.tabNames = []
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
        self.tabHolderWidget = QTabWidget(self.mainWindow)

        # Set up main window
        self.mainWindow.show()
        self.mainWindow.setCentralWidget(self.tabHolderWidget)
        self.mainWindow.setWindowTitle(self.title)
        self.mainWindow.resize(1920, 1080)

        self.serial_port_menu = QMenu()
        self.modules_menu = QMenu()
        self.playback_source_menu = QMenu()

        self.widgetClasses = {"Annunciator Panel": annunciator_panel.AnnunciatorPanel,
                              "Control Station Status": control_station_status.ControlStationStatus,
                              "Flight Display": flight_display.FlightDisplay,
                              "Map Widget": map_widget.MapWidget,
                              "Reconfigure": reconfigure_widget.ReconfigureWidget,
                              "Console": simple_console_widget.SimpleConsoleWidget,
                              "CLI Console": complete_console_widget.CompleteConsoleWidget,
                              "Diagnostic Panel": text_box_drop_down_widget.TextBoxDropDownWidget,
                              "Vehicle Status": vehicle_status_widget.VehicleStatusWidget,
                              "Video Panel": video_widget.VideoWidget,
                              "Graph Widget": graph_widget.GraphWidget,
                              "Pyro Display": pyro_display_widget.PyroWidget,
                              "Local Sim Helper": local_sim_widget.LocalSimWidget,
                              "Line Cutter Control": line_cutter_control.LineCutterControl,
                              }  # List of classes of widgets that can be dynamically created

        self.tabClasses = {"Settings": SettingsTab,
                           "Diagnostic": DiagnosticTab,
                           "Rocket Primary": RocketPrimaryTab,
                           "Graph": GraphsTab,
                           "Empty": TabCommon,
                           }  # List of tabs that can be dynamically created

        self.application.setObjectName("Application")
        self.mainWindow.setObjectName("Main_Window")
        self.mainWindow.menuBar().setObjectName("Menu_Bar")
        self.tabHolderWidget.setObjectName("Tab_Holder")
        self.tabHolderWidget.tabBar().setObjectName("Tab_Bar")

        # Generate a random title from this list
        # I don't know why I did this
        titles = ["DPF Ground Station", "Make sure the pointy end is facing up", "This title intentionally left blank", "Don't crash the rocket"]
        self.title = random.choice(titles)

        # Add callback to clear console
        self.addCallback("clear_console", self.clearConsole)
        self.addCallback("enable_module", self.enableModuleCallback)

        # Other setup tasks
        self.setThemeByName("Dark")
        self.setUpMenuBar()

    def run(self):
        # QTimer to run the update method
        timer = QTimer()
        timer.timeout.connect(self.updateGUI)
        timer.start(20)

        # Run (blocks until GUI closes)
        self.application.exec_()

        # This happens after the GUI closes
        self.stop()

    def setUpMenuBar(self):
        """Create menu bar"""

        # Get main menu bar object
        menu_bar = self.mainWindow.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Quit", self.stop)

        # Menu bar to add new widgets
        insert_menu = menu_bar.addMenu("Insert")

        widget_menu = insert_menu.addMenu("Widget into current tab")
        sorted_keys = list(self.widgetClasses.keys())
        sorted_keys.sort()
        for item in sorted_keys:
            widget_menu.addAction(item, lambda name=item: self.makeNewWidgetInCurrentTab(name))

        widget_menu_2 = insert_menu.addMenu("Widget as own window")
        for item in sorted_keys:
            widget_menu_2.addAction(item, lambda name=item: self.makeNewWidgetInNewWindow(name))

        tab_menu = insert_menu.addMenu("New Tab")
        sorted_tabs = list(self.tabClasses.keys())
        sorted_tabs.sort()
        for item in sorted_tabs:
            tab_menu.addAction(item, lambda name=item: self.addTabByTabType(name, None))

        tab_menu = insert_menu.addMenu("New Tab as own window")
        for item in sorted_tabs:
            tab_menu.addAction(item, lambda name=item: self.addTabByTabType(name, None, own_window=True))

        # Menu bar to change theme
        theme_menu = menu_bar.addMenu("Theme")
        for theme in THEMES:
            theme_menu.addAction(theme, lambda theme_name=theme: self.setThemeByName(theme_name))

        # Menu bar to set serial port
        # Because the available serial ports and data interfaces change after this class is created, we run a method every time we create the menu
        self.serial_port_menu = menu_bar.addMenu("Serial Port")
        self.serial_port_menu.aboutToShow.connect(self.refreshSerialPorts)  # aboutToShow runs before the menu is created

        # Menu bar to enable/disable data interfaces
        self.modules_menu = menu_bar.addMenu("Modules")
        self.modules_menu.aboutToShow.connect(self.refreshDataInterfaces)

        self.playback_source_menu = menu_bar.addMenu("Playback Options")
        self.playback_source_menu.aboutToShow.connect(self.playbackOptionsMenu)

    def setActiveSerialPort(self, port_name):
        self.callback_queue.append(["set_serial_port", port_name])

    def toggleModuleEnabledState(self, module_name):
        if module_name in self.module_dictionary:
            interface = self.module_dictionary[module_name]
            self.enableOrDisableModule(module_name, not interface.enabled)
        else:
            self.updateConsole("Module {} does not exist".format(module_name), 2)

    def enableOrDisableModule(self, module_name, enabled):
        if module_name in self.module_dictionary:
            interface = self.module_dictionary[module_name]
            interface.setEnabled(enabled)

            # If we just enabled module that should be by itself, disable the others
            if interface.primary_module and interface.enabled:
                for target_module_name in self.module_dictionary:
                    if target_module_name != module_name and self.module_dictionary[target_module_name].primary_module:
                        self.module_dictionary[target_module_name].setEnabled(False)
        else:
            self.updateConsole("Module {} does not exist".format(module_name), 2)

    def refreshDataInterfaces(self):
        self.modules_menu.clear()

        for interfaceName in self.module_dictionary:
            interface = self.module_dictionary[interfaceName]
            if interfaceName in self.hidden_modules:
                pass
            elif interface.enabled:
                self.modules_menu.addAction("Disable {}".format(interfaceName), lambda target_interface=interfaceName: self.toggleModuleEnabledState(target_interface))
            else:
                self.modules_menu.addAction("Enable {}".format(interfaceName), lambda target_interface=interfaceName: self.toggleModuleEnabledState(target_interface))

    def refreshSerialPorts(self):
        serial_ports = [comport for comport in serial.tools.list_ports.comports()]
        self.serial_port_menu.clear()
        for port in serial_ports:
            self.serial_port_menu.addAction("{0}: {1}".format(port.device, port.description), lambda portName=port.device: self.setActiveSerialPort(portName))

    def playbackOptionsMenu(self):
        self.playback_source_menu.clear()
        for option in self.playback_data_sources:
            self.playback_source_menu.addAction(option, lambda option_name=option: self.setCurrentPlaybackOption(option_name))

    def setCurrentPlaybackOption(self, option):
        self.current_playback_source = option

    def updateGUI(self):
        """Runs in GUI thread every 20ms"""
        if self.GUIStopCommanded:
            self.stop()

        start_time = time.time()

        recorded_data_dict = {}

        # Get data from interfaces
        for interface in self.module_dictionary:
            interface_object = self.module_dictionary[interface]
            if interface_object.hasRecordedData():
                interface_runs = ["{0} | {1}".format(interface, run) for run in interface_object.getRunNames()]
                self.playback_data_sources = list(set(self.playback_data_sources + interface_runs))
                self.playback_data_sources.sort()
            self.updateDatabaseDictionary(interface_object.getDataDictionary().copy())

            if self.current_playback_source.split(" | ")[0] == interface:
                run_name = self.current_playback_source.split(" | ")[1]
                recorded_data_dict = interface_object.getSpecificRun(run_name)

        # Send full database dictionary back to the data interfaces
        for interface in self.module_dictionary:
            self.module_dictionary[interface].setFullDataDictionary(copy.deepcopy(self.database_dictionary))
            self.updateReconfigureOptions(Constants.primary_reconfigure, self.module_dictionary[interface].getReconfigureDictionary())

        # Update placeholder widgets
        for widget in self.placeHolderList:
            widget.update()

        # Update tabs
        active_tab = self.getActiveTabObject()
        for tab in self.tabObjects:
            self.callback_queue += tab.updateVehicleData(self.database_dictionary, self.ConsoleData, self.updated_data_dictionary, recorded_data_dict)

        # set window title
        tab_index = self.tabHolderWidget.currentIndex()
        active_tab = self.tabHolderWidget.tabText(tab_index)
        self.mainWindow.setWindowTitle("[{0}] - {1}".format(active_tab, self.title))

        # Process callbacks
        self.processCallbacks()

        # Set every field as not-updated
        for key in self.updated_data_dictionary:
            self.updated_data_dictionary[key] = False

        self.database_dictionary[Constants.loop_time_key] = time.time() - start_time
        self.updated_data_dictionary[Constants.loop_time_key] = True

    def updateReconfigureOptions(self, database_dict_target, new_data):
        if database_dict_target not in self.database_dictionary:
            self.database_dictionary[database_dict_target] = {}

        self.database_dictionary[database_dict_target].update(new_data)

    def updateDatabaseDictionary(self, new_dict):
        for key in new_dict:
            self.database_dictionary[key] = new_dict[key]
            self.updated_data_dictionary[key] = True

    def createWidgetFromName(self, widget_name, parent=None, in_new_window=False):
        """Will create any widget from its file name!"""
        if widget_name not in self.widgetClasses:
            print("No widget of type {}".format(widget_name))
            return QWidget(parent)  # Kind of a hack
        try:
            if in_new_window:
                widget = self.widgetClasses[widget_name]()
            else:
                widget = self.widgetClasses[widget_name](parent)
            return widget
        except all as e:
            print("Dynamically creating {} type widgets is not supported yet".format(widget_name))
            print(e)
            return QWidget(parent)

    def makeNewWidgetInCurrentTab(self, name):
        if name in self.widgetClasses:
            activeTab = self.getActiveTabObject()
            if activeTab is not None:
                activeTab.addWidget(self.createWidgetFromName(name, parent=activeTab))
                activeTab.updateTheme()
        else:
            print("No widget named {}".format(name))

    def makeNewWidgetInNewWindow(self, name):
        if name in self.widgetClasses:
            activeTab = self.getActiveTabObject()
            if activeTab is not None:
                activeTab.addWidget(self.createWidgetFromName(name, parent=activeTab, in_new_window=True))
                activeTab.updateTheme()
        else:
            print("No widget named {}".format(name))

    def getActiveTabObject(self) -> TabCommon:
        tab_index = self.tabHolderWidget.currentIndex()
        active_tab = self.tabHolderWidget.tabText(tab_index)

        if active_tab in self.tabNames:
            return self.tabObjects[self.tabNames.index(active_tab)]
        else:
            return None

    def addTabByTabType(self, tab_type: str, tab_name, own_window=False):
        if tab_name is None:
            tab_name = "{0} - {1}".format(tab_type, len(self.tabObjects))

        if tab_type in self.tabClasses:
            tab_class = self.tabClasses[tab_type]
            self.addVehicleTab(tab_class, tab_name, own_window)
        else:
            print("Don't have tab configuration for vehicle type {}".format(tab_type))

    def addVehicleTab(self, tab, vehicle_name: str, own_window=False):
        if not own_window:
            new_tab_object = tab(vehicle_name, parent=self.tabHolderWidget)
            self.tabHolderWidget.addTab(new_tab_object, vehicle_name)
            self.tabHolderWidget.setCurrentIndex(self.tabHolderWidget.count() - 1)
            self.tabHolderWidget.setCurrentIndex(1)
        else:
            new_tab_object = tab(vehicle_name)
            new_tab_object.show()

        self.tabObjects.append(new_tab_object)
        self.tabNames.append(vehicle_name)

        self.placeHolderList.append(placeholder.Placeholder(new_tab_object))  # Something needs to be updating for the GUI to function, so we make a silly thing to always do that
        new_tab_object.setTheme(self.backgroundColor, self.widgetBackgroundColor, self.textColor, self.headerTextColor, self.borderColor)

    def setThemeByName(self, name: str):
        if name in THEMES:
            theme = THEMES[name]
            self.setTheme(theme[0], theme[1], theme[2], theme[3], theme[4])
        else:
            print("No Theme named {}".format(name))

    def setTheme(self, background: str, widget_background: str, text: str, header_text: str, border: str):
        """
        Sets theme from given color strings.  Currently the only accpted format for color strings is rgb(red,green,blue), but I'm going to add more at some point.

        :param background: Background color for the GUI
        :param widget_background: Widget color
        :param text: Primary text color
        :param header_text: Header text color
        :param border: Widget border color
        """

        self.backgroundColor = get_well_formatted_rgb_string(background)
        self.widgetBackgroundColor = get_well_formatted_rgb_string(widget_background)
        self.textColor = get_well_formatted_rgb_string(text)
        self.headerTextColor = get_well_formatted_rgb_string(header_text)
        self.borderColor = get_well_formatted_rgb_string(border)

        [red, green, blue] = get_rgb_from_string(background)
        slightly_darker_color = format_rgb_string(max(red - 10, 0), max(green - 10, 0), max(blue - 10, 0))

        self.mainWindow.setStyleSheet("QWidget#" + self.mainWindow.objectName() + "{" + make_stylesheet_string("background", slightly_darker_color) + make_stylesheet_string("color", self.textColor) + "}")
        self.tabHolderWidget.setStyleSheet("QWidget#" + self.tabHolderWidget.objectName() + "{" + make_stylesheet_string("background", self.backgroundColor) + make_stylesheet_string("color", self.textColor) + "}")
        self.mainWindow.menuBar().setStyleSheet("QWidget#" + self.mainWindow.menuBar().objectName() + "{" + make_stylesheet_string("background", slightly_darker_color) + make_stylesheet_string("color", self.textColor) + "}")
        self.tabHolderWidget.tabBar().setStyleSheet("QWidget#" + self.tabHolderWidget.tabBar().objectName() + "{" + make_stylesheet_string("background", slightly_darker_color) + make_stylesheet_string("color", self.textColor) + "}")

        if sys.platform == "win32":
            self.tabHolderWidget.tabBar().setStyleSheet("QTabBar::tab{ background: " + get_well_formatted_rgb_string(background) + "; color: " + get_well_formatted_rgb_string(text) + "}")  # Seems to sort of fix tab bar coloring issues on windows
            self.tabHolderWidget.setStyleSheet("background: " + get_well_formatted_rgb_string(background) + ";border: " + get_well_formatted_rgb_string(background))

        for tab in self.tabObjects:
            tab.setTheme(self.backgroundColor, self.widgetBackgroundColor, self.textColor, self.headerTextColor, self.borderColor)

    def updateConsole(self, value, level):
        self.ConsoleData = ([[value, level]] + self.ConsoleData)[:40]

    def enableModuleCallback(self, data):
        data = data.split(",")
        module_name = data[0]
        module_enabled = data[1].lower() == "true"
        self.enableOrDisableModule(module_name, module_enabled)

    def processCallbacks(self):
        callbacks = copy.deepcopy(self.callback_queue)
        self.callback_queue = []

        for callback in callbacks:
            if callback[0] in self.callbackFunctions:
                callback_list = self.callbackFunctions[callback[0]]
                for callback_function in callback_list:
                    callback_function(callback[1])  # <sarcasm>What amazingly clean code</sarcasm>
            else:
                pass
                # print("{} isn't a valid callback".format(callback[0]))  # Debugging code
                # print(self.callbackFunctions.keys())

    def addCallback(self, target, callback):
        if target not in self.callbackFunctions:
            self.callbackFunctions[target] = []

        self.callbackFunctions[target].append(callback)

    def addModule(self, interface_name: str, interface_class: type(ThreadedModuleCore), enabled=True, hide_toggle=False):
        try:
            start_time = time.time()

            interface_object = interface_class()
            interface_object.setConsoleCallback(self.updateConsole)
            interface_object.setEnabled(enabled)

            interface_object.start()

            callbacks = interface_object.getCallbacksToAdd()
            for callback in callbacks:
                if len(callback) == 2:
                    self.addCallback(callback[0], callback[1])

            if hide_toggle:
                self.hidden_modules.append(interface_name)

            self.module_dictionary[interface_name] = interface_object  # Append last so it doesn't get appended if any errors pop up

            delta_time = time.time() - start_time
            self.module_load_time_dictionary[interface_name] = delta_time
        except Exception as e:  # Should catch a lot of errors loading in modules
            error_string = "Could not load module {0} of type {1}: {2}".format(interface_name, interface_class, e)
            print(error_string)
            self.updateConsole(error_string, 2)

    def clearConsole(self, _):  # Need a empty arg to fit with callback system
        self.ConsoleData = [[]]

    def stop(self):
        for interface in self.module_dictionary:
            self.module_dictionary[interface].stop()

        self.application.exit()
