"""
Central GUI sequencer

Has all the thread control for the GUI
"""

import copy
import os
import random
import sys
import time

import serial.tools.list_ports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QTabWidget, QWidget

from qt_material import apply_stylesheet, list_themes

import src.data_helpers
from src.constants import Constants
from src.MainTabs.diagnostic_tab import DiagnosticTab
from src.MainTabs.graphs_tab import GraphsTab
from src.MainTabs.main_tab_common import TabCommon
from src.MainTabs.model_viewer import ModelViewer
from src.MainTabs.offload_tab import OffloadTab
from src.MainTabs.rocket_primary_tab import RocketPrimaryTab
from src.MainTabs.settings_tab import SettingsTab
from src.Modules.data_interface_core import ThreadedModuleCore
from src.Widgets import (
    annunciator_panel,
    board_usb_offloader_widget,
    complete_console_widget,
    control_station_status,
    flight_display,
    gl_display_widget,
    graph_widget,
    line_cutter_control,
    local_sim_widget,
    map_widget,
    placeholder,
    pyro_display_widget,
    reconfigure_widget,
    simple_console_widget,
    text_box_drop_down_widget,
    vehicle_status_widget,
    video_widget,
    navball_widget,
)

if sys.platform == "linux":  # I don't even know anymore
    if "QT_QPA_PLATFORM_PLUGIN_PATH" in os.environ:
        os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")  # https://stackoverflow.com/questions/63829991/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it


def serial_port_callback_name(device):
    return "set_{}_serial_port".format(device)


CUSTOM_THEMES = list(map(lambda it: os.path.join("themes", it), os.listdir("themes")))

class DPFGUI:
    def __init__(self):
        """
        Main GUI Class
        """

        self.GUIStopCommanded = False  # Currently not used, but can be set to True to stop the GUI in the correct thread

        # This could use some restructuring
        # Big dictionary that contains the overall database all the widgets draw from
        self.database_dictionary = {}
        # Tracks which keys are new since the last GUI loop
        self.updated_data_dictionary = {}
        # List of log messages in primary console [[message, level], []...]
        self.ConsoleData = [[]]
        # Dictionary of list of callback functions that can be called from any widget.  These are typically added by modules.  {callback_name: [function_pointer, pointer, ...], ...}
        self.callbackFunctions = {}
        # List of callback function names to call.  These are called in the GUI thread during the update() function
        self.callback_queue = []
        # Dictionary of module objects {module_name: module_object, ...}
        self.module_dictionary = {}
        # Dictionary of module load times {module_name: load_time, ...}
        self.module_load_time_dictionary = {}
        # List of modules that we don't provide a drop-down option to enable or disable
        self.hidden_modules = []
        self.playback_data_sources = []
        self.current_playback_source = ""

        self.tabNames = []
        self.placeHolderList = []
        self.tabObjects = []

        self.title = ""

        self.application = QApplication([])  # PyQt Application object
        self.mainWindow = QMainWindow()  # PyQt MainWindow widget
        self.tabHolderWidget = QTabWidget(self.mainWindow)  # TabHolderWidget to contain tabs

        # Set up main window
        self.mainWindow.show()
        self.mainWindow.setCentralWidget(self.tabHolderWidget)
        self.mainWindow.setWindowTitle(self.title)
        self.mainWindow.resize(1920, 1080)

        # Make some menus that we'll need later
        self.serial_devices_menu = QMenu()
        self.modules_menu = QMenu()
        self.playback_source_menu = QMenu()
        self.serial_devices = []  # List of names of devices that use a serial port
        self.serial_devices_ports = {}  # Dictionary of which ports said device is using {device: port, ...}

        # List of classes of widgets that can be dynamically created
        self.widgetClasses = {
            "Annunciator Panel": annunciator_panel.AnnunciatorPanel,
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
            "3d Viewer": gl_display_widget.ThreeDDisplay,
            "Offload GUI": board_usb_offloader_widget.BoardCliWrapper,
            "CLI USB Console": complete_console_widget.CLIUSBInterface,
            "Navball Widget": navball_widget.NavballWidget,
        }

        # List of tabs that can be dynamically created
        self.tabClasses = {
            "Settings": SettingsTab,
            "Diagnostic": DiagnosticTab,
            "Rocket Primary": RocketPrimaryTab,
            "Graph": GraphsTab,
            "Empty": TabCommon,
            "Model Viewer": ModelViewer,
            "Offload": OffloadTab,
        }

        # Set some object names for all the core stuff
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
        self.setUpMenuBar()

    def run(self):
        """
        Function called in main when its ready to run the GUI

        Sets up the update timer, calls the PyQt exec_ function, and closes down the GUI when done
        """

        self.setThemeByName("dark_cyan.xml")

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
        for theme in self.getThemes():
            theme_menu.addAction(theme, lambda theme_name=theme: self.setThemeByName(theme_name))

        # Menu bar to set serial port
        # Because the available serial ports and data interfaces change after this class is created, we run a method every time we create the menu
        self.serial_devices_menu = menu_bar.addMenu("Serial Devices")
        self.serial_devices_menu.aboutToShow.connect(self.refreshSerialDevices)  # aboutToShow runs before the menu is created

        # Menu bar to enable/disable data interfaces
        self.modules_menu = menu_bar.addMenu("Modules")
        self.modules_menu.aboutToShow.connect(self.refreshDataInterfaces)

        self.playback_source_menu = menu_bar.addMenu("Playback Options")
        self.playback_source_menu.aboutToShow.connect(self.playbackOptionsMenu)

    def setActiveSerialPort(self, port_name, device_name):
        """
        Function to queue up a callback to change serial port
        The actual callback is provided by the module that interfaces with the serial device
        """

        callback_name = serial_port_callback_name(device_name)
        self.callback_queue.append([callback_name, port_name])
        self.serial_devices_ports[device_name] = port_name

        if port_name == "":  # Don't need to do anything more if we're disconnecting this device
            return

        # Otherwise, make sure no one else is using the port
        for device in self.serial_devices_ports:
            port = self.serial_devices_ports[device]
            if port == port_name and device != device_name:
                callback = serial_port_callback_name(device)
                self.callback_queue.append([callback, ""])
                self.serial_devices_ports[device] = ""

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

    def refreshSerialDevices(self):
        serial_ports = [comport for comport in serial.tools.list_ports.comports()]
        self.serial_devices_menu.clear()

        for device in self.serial_devices:
            device_menu = self.serial_devices_menu.addMenu(device)

            for port in serial_ports:
                device_menu.addAction("{0}: {1}".format(port.device, port.description), lambda portName=port.device, device_name=device: self.setActiveSerialPort(portName, device_name))
                device_menu.addAction("Disconnect", lambda portName="", device_name=device: self.setActiveSerialPort(portName, device_name))  # Kind of a hack

    def playbackOptionsMenu(self):
        self.playback_source_menu.clear()
        for option in self.playback_data_sources:
            self.playback_source_menu.addAction(option, lambda option_name=option: self.setCurrentPlaybackOption(option_name))

    def setCurrentPlaybackOption(self, option):
        self.current_playback_source = option

    def updateGUI(self):
        """
        Runs in GUI thread every 20ms.  Gets new data updates from modules, provides them with the full database, updates each tab, and handles running any callbacks.
        """

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
            self.updateDatabaseDictionary(interface_object.getDataDictionary())

            if self.current_playback_source.split(" | ")[0] == interface:
                run_name = self.current_playback_source.split(" | ")[1]
                recorded_data_dict = interface_object.getSpecificRun(run_name)

        # Send full database dictionary back to the data interfaces
        for interface in self.module_dictionary:
            try:
                self.module_dictionary[interface].setFullDataDictionary(self.database_dictionary)
                self.updateReconfigureOptions(Constants.primary_reconfigure, self.module_dictionary[interface].getReconfigureDictionary())
            except RuntimeError:  # Sometimes there's a "dictionary changed size during iteration" error here that I don't want to debug
                pass

        # Update placeholder widgets
        for widget in self.placeHolderList:
            widget.update()

        # Update tabs
        tab_index_to_remove = -1
        for tab in self.tabObjects:
            self.callback_queue += tab.updateVehicleData(self.database_dictionary, self.ConsoleData, self.updated_data_dictionary, recorded_data_dict)
            if tab.isClosed:
                tab_index_to_remove = self.tabObjects.index(tab)

        if tab_index_to_remove != -1:  # Can't do this in the loop above, because python freaks when you change the size of a list while iterating through it
            self.tabObjects.pop(tab_index_to_remove)
            self.placeHolderList.pop(tab_index_to_remove)

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

    def updateDatabaseDictionary(self, new_dict: dict):
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
        else:
            print("No widget named {}".format(name))

    def makeNewWidgetInNewWindow(self, name):
        if name in self.widgetClasses:
            activeTab = self.getActiveTabObject()
            if activeTab is not None:
                activeTab.addWidget(self.createWidgetFromName(name, parent=activeTab, in_new_window=True))
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

    def getThemes(self):
        return list_themes() + CUSTOM_THEMES

    def setThemeByName(self, name: str):
        if name in self.getThemes():
            apply_stylesheet(self.application, theme=name)
            self.updateAfterThemeSet()
        else:
            print("No Theme named {}".format(name))

    def updateAfterThemeSet(self):
        self.application.setStyleSheet(self.application.styleSheet() + "\nQSlider:horizontal { background: none; } QSlider:horizontal { background: none; }")

        for tab in self.tabObjects:
            tab.updateAfterThemeSet()

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

            serial_devices = interface_object.getSerialDevices()
            for device in serial_devices:
                callback_name = serial_port_callback_name(device)
                callback_function = serial_devices[device]
                self.addCallback(callback_name, callback_function)
                if device not in self.serial_devices:
                    self.serial_devices.append(device)
                    self.serial_devices_ports[device] = ""  # Want to start everything up unconnected
                    self.setActiveSerialPort("", device)  # Force the module to comply with our demands

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
